

# Italian Phonetic Alphabet - a Telegram Bot
## _by Lucas Gonzalez Zan_



 <img src="logo.jpg"  width="140" height="35" href="https://www.linkedin.com/in/lucasgonzalezzan" />


This is a Telegram Bot designed to spell out using Italian cities and output a voice message with the spelling in Italian.

 <img src="link.jpg"  width="170" height="240" border="1" align="center" />

Scan to try live or follow: https://t.me/ItalianAlphabetbot

## Features

The bot accepts the following commands from any Telegram chat:

- /start 	---	Welcome message
- /help  	---	Bring up in-line keyboard with commands
- /abc  	---	Ask for text to spell out [^1]
- /listen --- Generate voice reply from last spelling [^2]
- /info --- Return this source code link


[^1]: Uses the dictionary defined in "apidata", non [A-Z] characters are ignored 
[^2]: The ogg files in /audios are joint (with headers recalculated) 

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





## Tech

No special modules are needed, only an updated release of python for new features, such as `case`:

- python-3.10.2

The ogg files are joint by the `myogg` library, a custom class which splits ogg pages and headers. A joint valid stream is delivered by recalculating ogg headers and checksums. 

## Docker

Requires `python:3.10-alpine3.17` or higher.
In Dockerfile update your telegram token:
ENV TOKEN="1234567890:ABCDEFGHIJKMNLOPQRSTUVXYZabcdefghij"

```
sudo docker build -t italianalphabetbot . 
sudo docker run -d --name italianalphabetbot_1 italianalphabetbot 
```

## License



**It's Free Software :)**
