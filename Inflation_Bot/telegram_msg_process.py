import logging
import os
from datetime import datetime, timezone, timedelta

from telegram_pushing import push
from get_datos_gob_ar import ipc_poll

from json_file_rw import json_read, json_write
import apidata 

logger = logging.getLogger(__name__) #to change level see: logging.conf [logger_telegram_msg_process]


def data_handler(bottoken, msg):

    global chat_id, text, token 
    token = bottoken

    logger.debug(f"Last command was: {apidata.last_cmd!r}") 

    if 'callback_query' in msg and 'data' in msg['callback_query']:
        chat_id = int(msg['callback_query']['from']['id'])
        text = str(msg['callback_query']['data']).lower() 
        return call_handler()
    if 'message' in msg:
        chat_id = int(msg['message']['from']['id'])
        text = str(msg['message']['text']).lower() #ya vi si existe 
        if 'entities' in msg['message'] and msg['message']['entities'][0]['type'] == "bot_command":
            return cmd_handler()
        #'message' exits but not 'bot_commnad'
        elif apidata.last_cmd:
            return last_cmd_handler()
        else:
            return msg_handler()
    else: raise TypeError("No 'message' nor 'callback_query' fields in the dictionary!")

def call_handler():
    if text[0] == "/": return cmd_handler()
    else: return msg_handler()

def cmd_handler():

    match text:
        case "/start":            
            logger.info("Starting bot message processing. \n Loading JSON data from data/IPC.json")
            apidata.last_cmd = None #Mark Complete
            try: 
                apidata.ipc = json_read(apidata.home + "/data/IPC.json") 
            except FileNotFoundError:
                logger.exception("Failed to load JSON file at /start. Toca /update para actualizar.") #logs trace
                push(token, chat_id, "ERROR: Failed to load JSON file. Toca /update para actualizar.")
                return 404
            else:
                logger.debug(f"Loaded local file data/IPC.json: {apidata.ipc!r}")
                return push(token, chat_id, "Hola\\! \nToca */help* para menu de ayuda", MarkdownV2=True) 
            #MarkdownV2. At the same time these _ * [ ] ( ) ~ > # + - = | { } . ! characters must be escaped with the preceding character \.


        case "/help":
            apidata.last_cmd = None
            return push(token, chat_id, "Elige una opcion: ", 
                    {'inline_keyboard': [
                                        [{'text':"Calc",'callback_data':"/calc_anual"}, {'text':"Tiempo",'callback_data':"/time"}],
                                        [{'text':"Actualizar IPC",'callback_data':"/update"}]
                                        ]
                    })

        case ("/date" | "/time"):
            apidata.last_cmd = None
            tzinfoARG = timezone(timedelta(hours=-3))
            now = datetime.now(tzinfoARG)
            logger.debug(f"TIME: {now!r}")
            return push(token, chat_id,"Fecha: " + now.strftime('%d/%B/%Y') + "\nHora en Argentina: " + now.strftime('%H : %M : %S') )

        case "/update":
            apidata.last_cmd = None
            try:
                apidata.ipc, status = ipc_poll("2017-01-01")
                if not(200 <= status < 300): raise ValueError('ERROR: No fue posible obtener datos de IPC desde datos.gob.ar')
                
                if not(os.path.isdir (apidata.home + "/data")): os.mkdir(apidata.home + "/data") #if no dir, create it
                json_write(apidata.home + "/data/IPC.json", apidata.ipc)        
                logger.debug(f"Got {len(apidata.ipc)} values with status {status}, written to local file IPC.json") 

                #show proof all OK
                chunk = ""
                for i in apidata.ipc[len(apidata.ipc)-6:]:
                    chunk = chunk + i[0] + " - " + str(round(i[1]*100, 2)) + "%\n"
                return  push(token, chat_id, f"Actualizados datos de IPC desde datos.gob.ar \nUltimos 6 meses: \n{chunk}")  
            except (ValueError, TypeError) as e:
                apidata.ipc = None
                logger.exception(f"Got status {status}, ipc data {apidata.ipc!r}") 
                push(token, chat_id, f"ERROR: No fue posible obtener datos de IPC desde datos.gob.ar") 
                return 404

        case "/calc_anual":
            if apidata.ipc is None: 
                return push(token, chat_id, "No tengo datos de inflacion\\. \nPor favor toca */start* o */update*", MarkdownV2=True) 
            apidata.last_cmd = "/calc_anual"
            logger.debug(f"Setting Last command to: {apidata.last_cmd}")  
            return push(token, chat_id, f"Calcular % acumulado de cuantos meses?")      
            

        case _:
            apidata.last_cmd = None
            logger.warning(f"Couln't understand in cmd_handler: {text}")
            return push(token, chat_id,"Sorry, I didn't understand you")


def last_cmd_handler():

    match apidata.last_cmd:
        case "/calc_anual":
            try:
                logger.debug(f"text: {text}")
                meses = int(text) 
                logger.debug(f"Meses: {text}")
                if not(0 < meses <= len(apidata.ipc)): raise ValueError('Cantidad de meses fuera de rango')
                last = len(apidata.ipc)-1
                logger.debug(f"last: {last}")
                w = 1
                for i in range(meses):
                    w = (float(apidata.ipc[last-i][1]) + 1) * w
                    logger.debug(f"Step: {i}, accumulado {w}")
                total = (w - 1) * 100
                apidata.last_cmd = None #Mark Complete
                return push(token, chat_id, f"El la inflacion acumulada en {meses} meses es de {total:.2f}%") 

            except (ValueError, TypeError):
                logger.exception("Meses was not an int!")
                return push(token, chat_id, f"Por favor ingresa un numero *natural* de uno a {len(apidata.ipc)}", MarkdownV2=True) 
     

        case _:
            logger.warning(f"Couln't understand in last_cmd_handler: {text}")
            return push(token, chat_id,"Sorry, I didn't understand you")


def msg_handler():

    matches = ["hi", "hi", "hello", "hey", "hola", "ciao"]
    if any(x in text for x in matches):
        logger.debug(f"Usr HELLO message: {text}")
        return push(token, chat_id, "Buenos dias!")

    matches = ["time", "tiempo", "date", "hora", "tempo", "data", "fecha"]
    if any(x in text for x in matches):
        logger.debug(f"Usr TIME message: {text}")
        tzinfoARG = timezone(timedelta(hours=-3))
        now = datetime.now(tzinfoARG)
        return push(token, chat_id,"Fecha: " + now.strftime('%d - %B - %Y') + "\nHora en Argentina: " + now.strftime('%H : %M : %S') )
    
    if text in ["bye", "ttyl", "good bye", "adios", "arrivederci"]:
        logger.debug(f"Usr BYE message: {text}")
        return push(token, chat_id,"It was nice chatting with you. Bye!" )

    logger.warning(f"Couln't understand in msg_handler: {text}")
    return push(token, chat_id,"Sorry, I didn't understand you")

