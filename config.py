import logging

#LOG
LOG_LEVEL = logging.INFO
LOG_FILE = "attendancebot.log"

#Channels
#POSTING_CH_ID = 625402636509773836
POSTING_CH_ID = 595739675428388874 #Test channel
COMMAND_CH_ID = 595739675428388874

#Commands
COMMAND_START = "!event"
COMMAND_REFILL_SHEET = "!refill"

#Emojis
EMOJI_OK =	u"\U00002705" #✅
EMOJI_CANCEL = u"\U0000274E" #❎
EMOJI_SHRUG = u"\U0001F937" #🤷
ACTIVITY = "Goat Simulator"

#Roles that can invoke the commands
ALLOWED_ROLES = [594601296942596116]

#Array of days when meetings happen. 0 = Monday, 1 = Tuesday, etc.
MEET_DAYS = [3,6]

#Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets'] # If modifying these scopes, delete the file token.pickle.
SPREADSHEET_RANGE = 'Sheet1!A2:B'
SPREADSHEET_WRITE_RANGE = 'Sheet1!B{0}'

MSG_FINISHED_LOADING = "Logged on as {0}!" #Console message shown when the bot is ready to work
MSG_FETCH_ERROR = "Error fetching message with id {0}" #Console message shown when there's a failure fetching a message
MSG_CONFIRMATION = "Start attendance for {0} event?\n This will delete any current attendance data for the date on the sheet." #Chat message for confirming the event before continuing
MSG_LOG_MEET_START = "{0} started a meet." #Message for logging actions from the allowed roles
MSG_ATTENDANCE_REACT = "{0} attendance:\n✅ - Will assist\n❎ - Won't assist\n🤷 - Maybe"