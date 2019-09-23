import logging
import string
from secrets import SPREADSHEET_ID

#LOG
LOG_LEVEL = logging.INFO
LOG_FILE = "attendancebot.log"

#Channels
POSTING_CH_ID = 625402636509773836
#POSTING_CH_ID = 595739675428388874 #Test channel
COMMAND_CH_ID = 595739675428388874

#Commands
COMMAND_START = "!woe"
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
def letterLUT():
    dic = {}
    counter = 0
    for letter in string.ascii_uppercase:
        dic[counter] = letter
        counter += 1
    return dic
LETTER_LOOKUP = letterLUT()

#Sheets
SCOPES = ['https://www.googleapis.com/auth/spreadsheets'] # If modifying these scopes, delete the file token.pickle.
SHEET_TAB_NAME = 'INFO!' #Range where to search for user ids
SHEET_DATE_RANGE = SHEET_TAB_NAME+'A1:H1' #Range where to search for the date, keep it to a single row that starts at A. Currently only supports A-Z but expanding is trivial.
SHEET_DISCORD_COLUMN = SHEET_TAB_NAME+'I1:I300' #Range where to search for user ids
SHEET_CLEAN_RANGE = SHEET_TAB_NAME+'G2:H300' #Range to clean on event prompt
SHEET_ROW_OFFSET = 1

MSG_FINISHED_LOADING = "Logged on as {0}!" #Console message shown when the bot is ready to work
MSG_FETCH_ERROR = "Error fetching message with id {0}" #Console message shown when there's a failure fetching a message
MSG_CONFIRMATION = "Empezar a tomar lista para la woe del {0}?\nEsto va a borrar lo que este cargado en la spreadsheet de asistencia." #Chat message for confirming the event before continuing
MSG_LOG_MEET_START = "{0} started a meet." #Message for logging actions from the allowed roles
MSG_ATTENDANCE_REACT = "{0} woe, presentismo:\n✅ - Va a WoE\n❎ - No va a WoE\n🤷 - Posible pero no es seguro"
MSG_MISSING_USERNAME = "No encontramos el nombre {} en la planilla https://docs.google.com/spreadsheets/d/"+SPREADSHEET_ID+" .Agregate."