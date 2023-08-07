import logging
import os
from datetime import datetime, timezone, timedelta
from telegram_pushing import push, push_photo
from get_datos_gob_ar import ipc_poll
from calc_datos_gob_ar import cumulative_months, average_months, project_months
from json_file_rw import json_write, bin_read

import apidata 


logger = logging.getLogger(__name__) #to change level see: logging.conf [logger_telegram_msg_process]


def data_handler(token, msg):


    if 'callback_query' in msg and 'data' in msg['callback_query']:
        chat_id = int(msg['callback_query']['from']['id'])
        text = str(msg['callback_query']['data']).lower() 
        if chat_id not in apidata.last_cmd: apidata.last_cmd[chat_id] = None  #new user
        return call_handler(token, chat_id, text)
    if 'message' in msg:
        chat_id = int(msg['message']['from']['id'])
        text = str(msg['message']['text']).lower() #ya vi si existe 
        if chat_id not in apidata.last_cmd: apidata.last_cmd[chat_id] = None  #new user
        if 'entities' in msg['message'] and msg['message']['entities'][0]['type'] == "bot_command":
            return cmd_handler(token, chat_id, text)
        #'message' exits but not 'bot_commnad'
        elif apidata.last_cmd[chat_id]:
            return last_cmd_handler(token, chat_id, text)
        else:
            return msg_handler(token, chat_id, text)
    else: raise TypeError("No 'message' nor 'callback_query' fields in the dictionary!")

def call_handler(token, chat_id, text):
    if text[0] == "/": return cmd_handler(token, chat_id, text)
    else: return msg_handler(token, chat_id, text)

def cmd_handler(token, chat_id, text):

    match text:
        case "/start":            
            apidata.last_cmd[chat_id] = None #Mark Complete
            if len(apidata.ipc) < 2:    #default apidata is a list with one item, unless loaded IPC.json OK
                logger.info("No JSON file at /start. Toca /update para actualizar.") #logs trace
                return push(token, chat_id, "Failed to load JSON file\\. Toca */update* para actualizar", MarkdownV2=True)
            else:
                return push(token, chat_id, "Hola\\! \nToca */help* para menu de ayuda\nToca */calcanual* o */calcmeses* para promedios de inflacion\nToca */project* para proyectar la inflacion a futuro segun % promedio", MarkdownV2=True) 
            #MarkdownV2. At the same time these _ * [ ] ( ) ~ > # + - = | { } . ! characters must be escaped with the preceding character \.


        case "/help":   # reply with a keyboard with interactive buttons and commands (handled as a callback_query) 
            apidata.last_cmd[chat_id] = None
            return push(token, chat_id, "Elige una opcion: ", 
                    {'inline_keyboard': [
                                        [{'text':"Calc anual",'callback_data':"/calcanual"},{'text':"Calc promedio mensual",'callback_data':"/promedio"}],
                                        [{'text':"Calc X meses",'callback_data':"/calcmeses"},{'text':"Ver IPC datos.gob.ar",'callback_data':"/raw"}],
                                        [{'text':"Projectar X meses",'callback_data':"/project"},{'text':"Tiempo en Argentina",'callback_data':"/time"}],
                                        [{'text':"Actualizar IPC",'callback_data':"/update"}]
                                        ]
                    })

        case "/date" | "/time":
            apidata.last_cmd[chat_id] = None
            tzinfoARG = timezone(timedelta(hours=-3))
            now = datetime.now(tzinfoARG)
            logger.debug(f"TIME: {now!r}")
            return push(token, chat_id,"Fecha: " + now.strftime('%d/%B/%Y') + "\nHora en Argentina: " + now.strftime('%H : %M : %S') )

        case "/update": # update data from API
            apidata.last_cmd[chat_id] = None
            data, status = ipc_poll("2017-01-01") # call update with the starting date
            if not(200 <= status < 300): return push(token, chat_id, f"ERROR: No fue posible obtener datos de IPC desde datos.gob.ar") 
            try:    #verify data
                _ = data[0]     #at least one item in list
                for d, v, *_ in data:   #for every item, a date, a float, and whatever
                    _ = str(d)      #date
                    _ = float(v)    #IPC 
            except (ValueError, IndexError): #Some strings can be converted to float, for example 123.
                logger.exception(f"Got status {status}, ipc data {data!r}") 
                return push(token, chat_id, f"ERROR: No fue posible obtener datos de IPC desde datos.gob.ar") 

            apidata.ipc = data
            if not(os.path.isdir (apidata.home + "/data")): os.mkdir(apidata.home + "/data") #if no dir, create it
            b = json_write(apidata.home + "/data/IPC_updated.json", apidata.ipc)        
            logger.debug(f"Got {len(apidata.ipc)} values with status {status}, written to local file IPC_updated.json {b} bytes long") 
            #show proof all OK
            chunk = ""
            for i in apidata.ipc[-6:]:  #last 6 indices
                chunk = chunk + i[0] + " - " + str(round(i[1]*100, 2)) + "%\n"
            return  push(token, chat_id, f"Actualizados datos de IPC desde datos.gob.ar \nUltimos 6 meses: \n{chunk}")  

        case "/calcmeses":  # calculate cumulative % in X months
            apidata.last_cmd[chat_id] = "/calcmeses"
            logger.debug(f"Setting Last command to: {apidata.last_cmd[chat_id]}")  
            return push(token, chat_id, f"Calcular % acumulado de cuantos meses?") 

        case "/raw":        # see raw data of X months
            apidata.last_cmd[chat_id] = "/raw"
            logger.debug(f"Setting Last command to: {apidata.last_cmd[chat_id]}")  
            return push(token, chat_id, f"Mostrar datos de cuantos meses?") 

        case "/project":    # calculate future inflation using the last months inflation rate
            apidata.last_cmd[chat_id] = "/project"
            logger.debug(f"Setting Last command to: {apidata.last_cmd[chat_id]}")  
            return push(token, chat_id, f"Projectar inflacion usando cuantos meses?")         

        case "/calcanual": # calculate cumulative % in last trimesters 
            apidata.last_cmd[chat_id] = None
            return push(token, chat_id, 
                        f"Acumulado anual: {cumulative_months(12):.2f}%\n\n"  
                        f"Acumulado semestral: {cumulative_months(6,-1):.2f}% \nSemestre anterior: {cumulative_months(6,-6):.2f}%\n\n" 
                        f"Trimestral (1-3): {cumulative_months(3,-1):.2f}%\nTrimestral (4-6): {cumulative_months(3,-4):.2f}%\n"
                        f"Trimestral (7-9): {cumulative_months(3,-7):.2f}%\nTrimestral (10-12): {cumulative_months(3,-10):.2f}%"
                        )

        case "/promedio":   # calculate average inflation rate
            apidata.last_cmd[chat_id] = None
            return push(token, chat_id, 
                        f"Promedios calculados como (meses) √ (total)\ni.e. mismo % en cada mes en el periodo para igualar /calcanual\n\n"  
                        f"Promedio anual: {average_months(12):.2f}%\n\n"  
                        f"Promedio semestral: {average_months(6,-1):.2f}% \nSemestre anterior: {average_months(6,-6):.2f}%\n\n" 
                        f"Trimestral (1-3): {average_months(3,-1):.2f}%\nTrimestral (4-6): {average_months(3,-4):.2f}%\n"
                        f"Trimestral (7-9): {average_months(3,-7):.2f}%\nTrimestral (10-12): {average_months(3,-10):.2f}%"
                        )

        case "/ezeiza":     # send a joke picture
            apidata.last_cmd[chat_id] = None
            return push_photo(token, chat_id,f"La salida es Ezeiza #PLP", bin_read(apidata.home + "/data/nuevereinas.jpg"))

        case "/info":       # ask for source code
            return push(token, chat_id, f"Source code: https://github.com/lucasgonzalezzan/lucasgonzalezzan/tree/master/Inflation_Bot")

        case _:         # default, command not found
            apidata.last_cmd[chat_id] = None
            logger.warning(f"Couln't understand in cmd_handler: {text}")
            return push(token, chat_id,"Sorry, I didn't understand you")


def last_cmd_handler(token, chat_id, text):

    match apidata.last_cmd[chat_id]:
        case "/calcmeses":  # calculate cumulative % in X months
            try:
                apidata.last_cmd[chat_id] = None #Mark Complete
                logger.debug(f"text: {text}")
                meses = abs(int(text))       
                logger.debug(f"Meses: {text}")
                if not(0 < meses <= len(apidata.ipc)): raise ValueError('Cantidad de meses fuera de rango')
            except ValueError:
                logger.exception(f"Meses was not an int!")
                return push(token, chat_id, f"Por favor ingresa un numero *natural* de uno a {len(apidata.ipc)}", MarkdownV2=True) 
                
            return push(token, chat_id, f"La inflacion acumulada en {meses} meses es de {cumulative_months(meses):.2f}%\n Projectar /project") 

        case "/raw":        # see raw data of X months
            try:
                apidata.last_cmd[chat_id] = None #Mark Complete
                meses = abs(int(text))
                if not(0 < meses <= len(apidata.ipc)): raise ValueError('Cantidad de meses fuera de rango')
            except ValueError:
                logger.exception(f"Meses was not an int!")
                return push(token, chat_id, f"Por favor ingresa un numero *natural* de uno a {len(apidata.ipc)}", MarkdownV2=True) 
            chunk = ""
            for i in apidata.ipc[-meses:]:  #meses is +int
                chunk = chunk + i[0] + " - " + str(round(i[1]*100, 2)) + "%\n"
            return push(token, chat_id, f"Actualizados datos de IPC desde datos.gob.ar \nUltimos {meses} meses: \n{chunk}")  

        case "/project":    # calculate future inflation using the last X months average inflation rate
            try:
                apidata.last_cmd[chat_id] = None #Mark Complete
                meses = abs(int(text))
                if not(0 < meses <= len(apidata.ipc)): raise ValueError('Cantidad de meses fuera de rango')
            except ValueError:
                logger.exception(f"Meses was not an int!")
                return push(token, chat_id, f"Por favor ingresa un numero *natural* de uno a {len(apidata.ipc)}", MarkdownV2=True) 

            avg = average_months(meses)
            return push(token, chat_id, 
                        f"La inflacion acumulada en {meses} meses es de {cumulative_months(meses):.2f}%\nPara otros promedios usa /calcmeses\n\n"
                        f"Projeccion de inflacion con promedio de {avg:.2f}% en cada mes:\n"  
                        f"En 3 meses: {project_months(3, avg):.2f}%\n"  
                        f"En 6 meses: {project_months(6, avg):.2f}%\n" 
                        f"En un año: {project_months(12, avg):.2f}%\n"
                        f"En 2 años: {project_months(24, avg):.2f}%\n"
                        f"En 10 años: {project_months(120, avg):.2f}%\n"
                        f"Next stop /ezeiza"
                        )

        case _:
            logger.warning(f"Couln't understand in last_cmd_handler: {text}")
            return push(token, chat_id,"Sorry, I didn't understand you")

# simple messages replies
def msg_handler(token, chat_id, text):

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

