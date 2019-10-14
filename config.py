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
#COMMAND_START = "!attendance"
COMMAND_START = "!woe"
COMMAND_REFILL_SHEET = "!refill"
COMMANDS = [COMMAND_START, COMMAND_REFILL_SHEET]
COMMAND_REFILL_HISTORY = 20 #Amount of messages to check for in the channel backwards

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
SHEET_VERTICAL_LENGTH = 300
SHEET_DISCORD_COLUMN = SHEET_TAB_NAME+'I2:I'+str(2+SHEET_VERTICAL_LENGTH) #Range where to search for user ids
SHEET_CLEAN_RANGE = SHEET_TAB_NAME+'G2:H'+str(2+SHEET_VERTICAL_LENGTH) #Range to clean on event prompt
SHEET_ROW_OFFSET = 1

#English default
MSG_FINISHED_LOADING = "Logged on as {0}!" #Console message shown when the bot is ready to work
MSG_FETCH_ERROR = "Error fetching message with id {0}" #Console message shown when there's a failure fetching a message
#MSG_CONFIRMATION = "Start attendance for the {0} event?\nThis will clean up previous entries for the date on the spreadsheet." #Chat message for confirming the event before continuing
MSG_LOG_MEET_START = "{0} started a meet." #Message for logging actions from the allowed roles
#MSG_ATTENDANCE_REACT = "{0} Attendance:\n✅ - Will attend\n❎ - Won't attendE\n🤷 - Posible, but not sure"
#MSG_MISSING_USERNAME = "Couldn't find the user {} on the spreadsheet https://docs.google.com/spreadsheets/d/"+SPREADSHEET_ID+" . Add yourself if you can or contact the administrator."
MSG_MISSING_USERNAME_POST = "Missing user {} on the spreadsheet." #Message to post on the channel if a user is missing when using !refill
MSG_UNIMPLEMENTED_COMMAND = "The requested command {} is not yet implemented."
#MSG_DONE_REFILL = "Done refilling."

#Spanish adapted to local use
MSG_CONFIRMATION = "Empezar a tomar lista para la woe del {0}?\nEsto va a borrar lo que este cargado en la spreadsheet de asistencia." #Chat message for confirming the event before continuing
MSG_ATTENDANCE_REACT = "{0} woe, presentismo:\n✅ - Va a WoE\n❎ - No va a WoE\n🤷 - Posible pero no es seguro"
MSG_MISSING_USERNAME = "No encontramos el nombre {} en la planilla https://docs.google.com/spreadsheets/d/"+SPREADSHEET_ID+" .Agregate."
MSG_DONE_REFILL = "Actualizado."
