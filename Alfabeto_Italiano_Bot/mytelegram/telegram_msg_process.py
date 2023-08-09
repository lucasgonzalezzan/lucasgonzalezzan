import logging
from time import time
from .telegram_pushing import push, push_voice

from myogg.myogglib import join_ogg, Ogg
import apidata 

logger = logging.getLogger(__name__) #to change level see: logging.conf [logger_telegram_msg_process]


def data_handler(token, msg):

    def call_handler():
        if text[0] == "/": return cmd_handler()
        else: return msg_handler()

    def cmd_handler():
        nonlocal user 

        match text:
            case "/start":            
                user.last_cmd = None #Mark Complete
                return push(token, chat_id, "Ciao\\! I'm a bot to spell in italian alphabet\\. \nPress */help* for help menu\\. \nPress */abc* to translate\\.\nPress */listen* to convert text to audio\\.", MarkdownV2=True) 
                #MarkdownV2. At the same time these _ * [ ] ( ) ~ > # + - = | { } . ! characters must be escaped with the preceding character \.

            case "/help":
                user.last_cmd = None
                return push(token, chat_id, "I'm a bot to spell in italian alphabet.\nPress /start for a list of cmds\nOr choose an option:", 
                        {'inline_keyboard': [
                                            [{'text':"New translate",'callback_data':"/abc"}],
                                            [{'text':"Hear last translation",'callback_data':"/listen"}]
                                            ]
                        })

            case "/abc":
                user.last_cmd = "/abc"
                logger.debug(f"Setting Last command to: {user.last_cmd}")  
                return push(token, chat_id, f"Write your text now")      
            
            case "/listen":
                if not user.chars: 
                    user.last_cmd = "/abc"
                    logger.debug(f"Setting Last command to: {user.last_cmd}")  
                    return push(token, chat_id, f"First, write your text:")    

                results = list() #to check if push ended OK
                for i, word in enumerate(user.words):
                    audiolist = [apidata.oggfiles[c] for c in user.chars[i]]
                    logger.debug(f"For word {word} and ch {user.chars[i]} grabbed audio files as: {audiolist} objects")  
                    voice = join_ogg(audiolist) #Ogg object
                    # bin_write("join_ogg.ogg", voice.ogg)
                    status = push_voice(token, chat_id, f"{word}.ogg", file=voice.ogg ) #the 'ogg' method of 'voice' instance outputs a valid audio bytestream
                    results.append(True) if (200 <= status < 300) else results.append(False)
                return 200 if all(results) else 404 

            case "/info":
                return push(token, chat_id, f"Source code: https://github.com/lucasgonzalezzan/lucasgonzalezzan/tree/master/Alfabeto_Italiano_Bot")

            case _:
                user.last_cmd = None
                logger.warning(f"Couln't understand in cmd_handler: {text}")
                return push(token, chat_id,"Sorry, I didn't understand you")


    def last_cmd_handler():
        nonlocal user

        match user.last_cmd:        
            case "/abc":
                user.last_cmd = None #Mark Complete
                user.words = list()
                user.chars = list()
                results = list() #to check if push ended OK
                words = text.split()    
                for word in words:
                    upcase = word.upper() 
                    keys = list()
                    values = list()
                    for ch in upcase:
                        try:
                            values.append(apidata.abc_it[ch])
                        except KeyError as e: logger.debug(f"Not an A-Z character: {e}")
                        else:
                            keys.append(ch)
                    logger.debug(f"Usr characters: {keys}\nUsr values: {values}")

                    reply = f"For word {word}:"
                    for k, v in zip(keys, values):
                        reply += f"\n{k} as in {v}" # letter k as in city v
                    status = push(token, chat_id, f"{reply}")
                    results.append(True) if (200 <= status < 300) else results.append(False)

                    if not keys: continue   #if no valid key discard word and chars
                    user.chars.append(keys) #list of list of valid characters, no empty lists
                    user.words.append(word) #append word only if not empty list of chars

                logger.debug(f"User data: {vars(user)}")
                
                if all(results):
                    return push(token, chat_id, "Press */listen* to convert text to audio", MarkdownV2=True) 
                else: 
                    return 404

            case _:
                logger.warning(f"Couln't understand in last_cmd_handler: {text}")
                return push(token, chat_id,"Sorry, I didn't understand you")


    def msg_handler():
        nonlocal user

        matches = ["hi", "hi", "hello", "hey", "hola", "ciao"]
        if any(x in text for x in matches):
            logger.debug(f"Usr HELLO message: {text}")
            return push(token, chat_id, "Buenos dias!")


        if text in ["bye", "ttyl", "good bye", "adios", "arrivederci"]:
            logger.debug(f"Usr BYE message: {text}")
            return push(token, chat_id,"It was nice chatting with you. Bye!" )

        logger.warning(f"Couln't understand in msg_handler: {text}")
        return push(token, chat_id,"Sorry, I didn't understand you")


    try:    #1st check if 'message' in result, if KeyError then maybe it's a 'callback_query'
        chat_id = int(msg['message']['from']['id'])
        text = str(msg['message']['text']).lower() 
        if chat_id not in apidata.users: apidata.users[chat_id] = apidata.User()  #new user id
        user = apidata.users[chat_id]
        user.time = round(time())
        logger.debug(f"User data: {vars(user)}")

        try: #2nd check if bot_cmd, if KeyError then it's a simple message
            if msg['message']['entities'][0]['type'] == "bot_command": return cmd_handler()
        except KeyError as e:
            logging.debug(f"Not a bot_command: {e}")
        if apidata.users[chat_id].last_cmd: return last_cmd_handler()
        else:   return msg_handler()

    except KeyError as e:
        logging.debug(f"Not a simple message, trying callback_query: {e}") 


    try:    #check if 'callback_query' (from inline_keyboard) in 'result', if KeyError then Fail
        chat_id = int(msg['callback_query']['from']['id'])
        text = str(msg['callback_query']['data']).lower() 
        if chat_id not in apidata.users: return push(token, chat_id, "Ciao\\! I'm a bot to spell in italian alphabet\\. \nPress */help* for help menu\\. \nPress */abc* to translate\\.\nPress */listen* to convert text to audio\\.", MarkdownV2=True)  #new user
        user = apidata.users[chat_id]
        user.time = round(time())
        return call_handler()

    except KeyError as e:
        logging.debug(f"Not a callback_query: {e}") 

    logger.error(f"Couldn't process message: No 'message' nor 'callback_query' fields in the dictionary!")
    return 404