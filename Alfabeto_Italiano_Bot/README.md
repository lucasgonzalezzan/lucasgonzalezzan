# Argentinian Inflation - a Telegram Bot
## _by Lucas Gonzalez Zan_



 <img src="logo.jpg"  width="140" height="35" href="https://www.linkedin.com/in/lucasgonzalezzan" />


This is a Telegram Bot designed to gather official information from https://datos.gob.ar/ via API.


## Features

So far, the bot accepts the following commands from any Telegram chat:

- /start 	---	Restart bot
- /help  	---	Bring up inline keyboard with commnads
- /update  	---	Update Argentina's inflation rate "IPC" from datos.gob.ar
- /time  	---	Return current date and time in Argentina
- /calc_anual   ---	Given the number of months, calculate the cumulative inflation in that period 


<!-- [![](livebot.gif), align=center]()
 --> 

 <img src="livebot.gif"  width="754" height="480" border="1" align="center" />


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

Logging is saved in "bot.log". Optionally, we can set the debuggin level via the environment variable:
``` 
LOGLVL = DEBUG
export LOGLVL
```





## Tech

No special modules are needed, only an updated enviroment:

- python-3.10.2


## Installation

No packages needed


## License



**It's Free Software :)**