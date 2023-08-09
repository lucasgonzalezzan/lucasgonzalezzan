
# Argentinian Inflation - a Telegram Bot
## _by Lucas Gonzalez Zan_



 <img src="logo.jpg"  width="200" height="50" href="https://www.linkedin.com/in/lucasgonzalezzan" />


This is a Telegram Bot designed to gather official Argentinian inflation information from https://datos.gob.ar/ via API.

 <img src="link.jpg"  width="200" height="300" border="1" align="center" />

Scan to try live or follow: https://t.me/InflacionARGbot

## Features

The bot accepts the following commands from any Telegram chat:

- /start 	---	Welcome message
- /help  	---	Bring up in-line keyboard with commands
- /update  	---	Update Argentina's inflation rate "IPC" from datos.gob.ar
- /raw --- Verify IPC downloaded data, asks for how many months ago
- /time  	---	Return current date and time in Argentina
- /calcanual   --- Calculate the cumulative inflation in last year, semester and trimester
- /calcmeses  ---	Same as /calcanual  but asks for the period in months
- /promedio --- Calculate the average inflation per month for the year, semester and trimester
- /project --- Calculate the average inflation per month [^1] in a given periods an returns the inflation in next months/years, assuming constant inflation for each month
- /info --- Return this source code link

[^1]: The average is computed as the root of the total inflation (radicand) with radix as the number of months:
(<sup> months </sup> √ inf). In other words, a constant inflation of the average over the period of months results in the given total inflation.

<!-- [![](livebot.gif), align=center]()
 --> 

 <img src="livebot.gif"   border="1" align="center" />


## Usage

 ```
TOKEN=1234567890:ABCDEFGHIJKMNLOPQRSTUVXYZabcdefghij 
export TOKEN
python bot.py
```

Output log:
> 2022-03-16 17:03:28,297 - root - DEBUG - Payload is: {'ok': True, 'result': []} Status is: 200 <br/>
> 2022-03-16 17:03:28,297 - root - INFO - No messages to process. <br/>
> 2022-03-16 17:04:27,464 - root - INFO - Processing 1 menssages, last update_id was 441657297 <br/>
> 2022-03-16 17:04:27,464 - telegram_msg_process - DEBUG - Last command was: None <br/>

Logging is saved in "rotating.bot.log" which rotate logs every 2MB into a new file. Optionally, we can set the debugging level via the environment variable:
``` 
LOGLVL = DEBUG
export LOGLVL
```

## Dependencies

No special modules are needed, only an updated release of python for new features, such as `case`:

- python-3.10.2


## Docker

Requires `python:3.10-alpine3.17` or higher.
In Dockerfile update your telegram token:
ENV TOKEN="1234567890:ABCDEFGHIJKMNLOPQRSTUVXYZabcdefghij"

```
sudo docker build -t inflacionargbot . 
sudo docker run -d --name inflacionargbot_1 inflacionargbot 
```

## Workflow

### Workflow bot.py
The main process constantly polls telegrams servers for new messages. For each message, the data_handler in telegram_msg_process takes the request and answers to the corresponding user, via telegram's API.
<img src="workflow_inflation_bot.svg" width="600" border="1" align="center" />  

### Workflow telegram_msg_process.py
Telegram's API has different message types:
- Simple text message
- Command message, these start with '/'
- Callback query, these result from touching a graphic keyboard in the app (see InlineKeyboardButton [^2])

[^2]: InlineKeyboardButton represents a button structure in the app, see docs https://core.telegram.org/bots/api#inlinekeyboardbutton 

Finally, some commands need further information from the user. The app saves the user's ID.
<img src="workflow_inflation_msg_process.svg" width="600" border="1" align="center" />

## License


**It's Free Software :)**
