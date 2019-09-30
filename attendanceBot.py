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
        if message.channel.id == COMMAND_CH_ID and message.content in COMMANDS and self.isAllowed(message.author):
            await message.delete()
            if message.content == COMMAND_START:
                self.confirmationDate = nextMeet()
                msg = await self.commandsChannel.send(MSG_CONFIRMATION.format(self.confirmationDate))
                self.confirmationMessageID = msg.id
                toAwait = [msg.add_reaction(EMOJI_OK), msg.add_reaction(EMOJI_CANCEL)]
                await asyncio.gather(*toAwait)            
            elif message.content == COMMAND_REFILL_SHEET:
                await self.refill()
            else:
                await self.commandsChannel.send(MSG_UNIMPLEMENTED_COMMAND.format(message.content))

    #Function to create the message that will be reacted for attendance. Cleans the sheet also.
    async def postMeetPoll(self):
        self.cleanSheet()
        message = await self.postChannel.send(MSG_ATTENDANCE_REACT.format(self.confirmationDate))
        toAwait = [message.add_reaction(EMOJI_OK), message.add_reaction(EMOJI_CANCEL), message.add_reaction(EMOJI_SHRUG)]
        asyncio.gather(*toAwait)

    #Function to be called when the confirmation message for attendance has been reacted to
    async def handleConfirmation(self, payload):
        msg = await self.commandsChannel.fetch_message(self.confirmationMessageID)
        user = self.guilds[0].get_member(payload.user_id)
        userAccepted = payload.emoji.name == EMOJI_OK
        userCanceled = payload.emoji.name == EMOJI_CANCEL
        if userAccepted or userCanceled:
            if self.isAllowed(user):
                toAwait = []
                if userAccepted:
                    self.log(MSG_LOG_MEET_START.format(str(user)))
                    toAwait.append(self.postMeetPoll())
                self.confirmationMessageID = None
                toAwait.append(msg.delete())
                asyncio.gather(*toAwait)
                return                        
        return

    #Overload. See discord.py's Client documentation
    #payload members: message_id, user_id, channel_id, guild_id, emoji
    async def on_raw_reaction_add(self, payload):
        if payload.message_id == self.confirmationMessageID:
            await self.handleConfirmation(payload)
            return
        if payload.channel_id != POSTING_CH_ID:
            return
        msg = await self.postChannel.fetch_message(payload.message_id)
        if msg.author.id != self.user.id:
            return
        date = msg.content.split(" ")[0].strip().replace("-","/")
        user = self.guilds[0].get_member(payload.user_id)
        await self.assignReaction(user, payload.emoji.name, date)

    #Given a message id, refills the sheet and prints anyone with issues instead of dming
    async def refill(self):
        msg = None
        async for message in self.postChannel.history(limit=COMMAND_REFILL_HISTORY):
            if message.author.id == self.user.id:
                msg = message
                break
        if not msg:
            await self.commandsChannel.send("Baaa")
            return
        self.cleanSheet()
        date = msg.content.split(" ")[0].strip().replace("-","/")
        for reaction in message.reactions:
            users = await reaction.users().flatten()
            for user in users:
                if user.id != self.user.id:
                    await self.assignReaction(user, reaction.emoji, date, False)
        msg = await self.commandsChannel.send(MSG_DONE_REFILL)

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
    async def assignReaction(self,user,strEmoji,date,dmMissingUser=True):
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
            if dmMissingUser:
                await user.send(MSG_MISSING_USERNAME.format(strUser))
            else:
                await self.commandsChannel.send(MSG_MISSING_USERNAME_POST.format(strUser))

            
    def cleanSheet(self):
        self.sheetService.values().clear(spreadsheetId=SPREADSHEET_ID,range=SHEET_CLEAN_RANGE).execute()

if __name__ == '__main__':
    client = MyClient()
    client.run(BOT_TOKEN)

