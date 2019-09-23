#pip install -U google-api-python-client google-auth-httplib2 google-auth-oauthlib discord.py
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
import discord
from config import *
from secrets import *
import logging
import datetime
import asyncio

#Logger
logger = logging.getLogger('discord')
logger.setLevel(LOG_LEVEL)
handler = logging.FileHandler(filename=LOG_FILE, encoding='utf-8', mode='a')
handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))
logger.addHandler(handler)

def nextMeet():
    date = datetime.date.today()
    while date.weekday() not in MEET_DAYS:
        date += datetime.timedelta(1)
    return str(date)

class MyClient(discord.Client):

    def __init__(self):
        super().__init__(fetch_offline_members=True,activity=discord.Activity(name=ACTIVITY,type=discord.ActivityType.playing))
        self.loginToSheet()
        self.postChannel = None
        self.commandsChannel = None
        self.confirmationMessageID = None 
        self.confirmationDate = None

    #Method for logging things to the log
    def log(self, message):
        logger.info(message)

    #Overload. See discord.py's Client documentation
    async def on_ready(self):
        print(MSG_FINISHED_LOADING.format(self.user))
        self.postChannel = self.get_channel(POSTING_CH_ID)
        self.commandsChannel = self.get_channel(COMMAND_CH_ID)

    #Checks if the person is allowed to run the commands
    def isAllowed(self, author):
        for role in author.roles:
            if role.id in ALLOWED_ROLES:
                return True
        return False

    #Overload. See discord.py's Client documentation
    async def on_message(self, message):
        if message.channel.id == COMMAND_CH_ID and message.content == COMMAND_START and self.isAllowed(message.author):
            self.cleanBeforeInput()
            self.confirmationDate = nextMeet()
            msg = await self.commandsChannel.send(MSG_CONFIRMATION.format(self.confirmationDate))
            self.confirmationMessageID = msg.id
            toAwait = [msg.add_reaction(EMOJI_OK), msg.add_reaction(EMOJI_CANCEL), message.delete()]
            await asyncio.gather(*toAwait)            

    #Function to create the message that will be reacted for attendance
    async def postMeetPoll(self):
        message = await self.commandsChannel.send(MSG_ATTENDANCE_REACT.format(self.confirmationDate))
        toAwait = [message.add_reaction(EMOJI_OK), message.add_reaction(EMOJI_CANCEL), message.add_reaction(EMOJI_SHRUG)]
        asyncio.gather(*toAwait)

    #Overload. See discord.py's Client documentation
    #payload members: message_id, user_id, channel_id, guild_id, emoji
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == self.confirmationMessageID:
            msg = await self.commandsChannel.fetch_message(self.confirmationMessageID)
            user = self.guilds[0].get_member(payload.user_id)
            goAhead = payload.emoji.name == EMOJI_OK
            cancel = payload.emoji.name == EMOJI_CANCEL
            if goAhead or cancel:
                if self.isAllowed(user):
                    toAwait = []
                    if goAhead:
                        self.log(MSG_LOG_MEET_START.format(str(user)))
                        toAwait.append(self.postMeetPoll())
                    self.confirmationMessageID = None
                    toAwait.append(msg.delete())
                    asyncio.gather(*toAwait)
                    return                        
            return
        if payload.channel_id != POSTING_CH_ID:
            return
        msg = await self.postChannel.fetch_message(payload.message_id)
        if msg.author.id != self.user.id:
            return
        date = msg.content.split(" ")[0].strip().replace("-","/")
        user = self.guilds[0].get_member(payload.user_id)
        await self.assignReaction(user, payload.emoji.name, date)

    # Logs into the sheets api and assigns the service to self.sheetService
    def loginToSheet(self):
        creds = None
        # The file token.pickle stores the user's access and refresh tokens, and is
        # created automatically when the authorization flow completes for the first time.
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                creds = pickle.load(token)
        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    'credentials.json', SCOPES)
                creds = flow.run_local_server()
            # Save the credentials for the next run
            with open('token.pickle', 'wb') as token:
                pickle.dump(creds, token)
        service = build('sheets', 'v4', credentials=creds)
        self.sheetService = service.spreadsheets()

    #Assigns a reaction to the spreadsheet
    #User is the user as a an object
    #strEmoji the emoji as a string
    #Date is the date for the event as a string in "yyyy/mm/dd" format
    async def assignReaction(self,user,strEmoji,date):
        result = self.sheetService.values().get(spreadsheetId=SPREADSHEET_ID,range=SHEET_DATE_RANGE,majorDimension="COLUMNS").execute()
        values = result.get('values', [])
        dateColumn = ""
        if not values:
            print('No data found.')
            return
        else:
            for x in range(len(values)):
                if values[x][0] == date:
                    dateColumn = LETTER_LOOKUP[x]
        result = self.sheetService.values().get(spreadsheetId=SPREADSHEET_ID,range=SHEET_DISCORD_COLUMN).execute()
        discordColumn = result.get('values', [])
        if not discordColumn:
            print('No data found.')
            return
        userRow = 0
        strUser = str(user)
        for x in range(len(discordColumn)):
            if discordColumn[x] and discordColumn[x][0] == strUser:
                self.sheetService.values().update(spreadsheetId=SPREADSHEET_ID,range="{}{}{}".format(SHEET_TAB_NAME,dateColumn,x+SHEET_ROW_OFFSET),body={ "values" : [[strEmoji]] },valueInputOption="RAW").execute()
                return
        if userRow == 0:
            await user.send(MSG_MISSING_USERNAME.format(strUser))
            
    def cleanBeforeInput(self):
        self.sheetService.values().clear(spreadsheetId=SPREADSHEET_ID,range=SHEET_CLEAN_RANGE).execute()

if __name__ == '__main__':
    client = MyClient()
    client.run(BOT_TOKEN)

