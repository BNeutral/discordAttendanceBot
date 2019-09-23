# Requirements

* Create an application on Discord's developer portal: https://discordapp.com/developers/applications/
* Get credentials for usage of the google sheets API either by clicking the big blue button in this page https://developers.google.com/sheets/api/quickstart/python or at https://console.developers.google.com/. You should end up with a credentials.json file in the same directory
* Install pip (python packet manager) and run `pip install -U google-api-python-client google-auth-httplib2 google-auth-oauthlib discord.py`

# Setup

* Add the bot to your server using the link created at the discord dev page for the app, under OAuth2 submenu
* Modify config.py to your liking
* Create a secrets.py file with the content:

```
BOT_TOKEN = <your bot token here, as a string. for example "AabB123...">
SPREADSHEET_ID = <your spreadsheet id here, as a string "AabB23...">
```

* Spreadsheet IDs can be found in the url. Bot token in the discord dev page.

# Run

python ./attendanceBot.py

# Usage

Documentation pending.
