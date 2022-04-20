#!/usr/bin/env python3
'''Bot to spell out using Italian cities and output a voice message with the spelling in Italian


Usage:
    export token variables "TOKEN=1234567890:cmZoYW1sb3p0a3hudjF6endrMWt2a2p1cWx ; export TOKEN"
    python bot.py <offset>  #optionally to define last update

Author:
    Lucas Gonzalez Zan - 15.04.2022
'''

import logging
import logging.config
import os
import sys
from time import time

from mytelegram.telegram_msg_process import data_handler as handler
from mytelegram.telegram_polling import poll as poll
from myogg.myogglib import Ogg
from myfiles.json_file_rw import bin_read, bin_write

import apidata  


print("Running: ", sys.argv[0], flush=True) 

# Enabling logging
try:
    LOGLVL = os.getenv("LOGLVL") #result are str
    loglevels = ["NOTSET","DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if LOGLVL in loglevels: 
        logging.basicConfig(level=loglevels.index(LOGLVL)*10, #change to DEBUG/INFO/WARNING etc
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        logging.info("Loaded logging as defined in enviroment LOGLVL")        
    else:
        
        logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
        logging.info("Loaded logger from logging.conf")


except:
    logging.basicConfig(level=logging.DEBUG, #change to DEBUG/INFO/WARNING etc
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logging.info("Loaded logging from basicConfig")

logger = logging.getLogger() #root logger


TOKEN = os.getenv("TOKEN")
if TOKEN is None or len(TOKEN) != 46: #10 numeros + ':'' + 35 ch
    logger.error("No TOKEN specified \n Try sth like 'TOKEN=1234567890:cmZoYW1sb3p0a3hudjF6endrMWt2a2p1cWx ; export TOKEN; and run again'")
    sys.exit(1)
logging.debug(f"TOKEN is set.") 
apidata.home = os.getcwd().replace("\\","/") if os.name == 'nt' else os.getcwd() #returns str pero en Win turn '\'' to linux 
logging.debug(f"Current directory = {apidata.home!r}") 

if __name__ == '__main__':
    logger.info("Starting bot.")
    offset = sys.argv[1] if len(sys.argv) > 1 else 0 #ternary operator
    errors = 0
    

    logger.info("Setting things. Loading ogg files.")
    if not(os.path.isdir (apidata.home + "/audios")): raise SystemExit("No folder with audio files")
    apidata.oggfiles = dict()
    for f in "ABCDEFGHIJKMNLOPQRSTUVWXYZ":
        apidata.oggfiles[f] = Ogg(bin_read(apidata.home + "/audios/" + f + ".ogg"))
    logger.info(f"Bot started")

    while errors < 100:
        now = round(time())
        for user in list(apidata.users.keys()): 
            if now - apidata.users[user].time > 60*5: #remove user after 5min
                logger.debug(f"Removing user_id: {user} with time {apidata.users[user].time} less than {now}")
                apidata.users.pop(user)
        logger.debug(f"Number of Users {len(apidata.users)} IDs: {apidata.users.keys()}")
                
        try:
            payload, status = poll(TOKEN, offset) #"By default, updates starting with the earliest unconfirmed update are returned. An update is considered confirmed as soon as getUpdates is called with an offset higher than its update_id" 
            if not(200 <= status < 300): 
                errors += 1
                logger.error(f"Polling returned status not 2XX: {status!r}")
                logger.error(f"Errors counted while handling data: {errors:d}")
                continue #returns the control to the beginning of the loop
            logger.debug(f"Payload is: {payload!r} Status is: {status!r}") #valor de result es una lista, y dentro dict
            try:  
                logger.info(f"Processing {len(payload['result']):d} menssages")
                for msg in payload['result']: #if not 'result' will raise KeyError, no IndexError because of the for (i.e. if len == 0 does nothing)
                    offset = int(msg['update_id']) +1   #poll with higher offset so as to "Confirm messages"
                    status = handler(TOKEN, msg) #returns response.status
                    logger.debug(f"Data_handler message ID:{msg['update_id']:d} Status is: {status!r}")
                    if not(200 <= status < 300): 
                        errors += 1
                        logger.error(f"telegram_msg_process data_handler returned: {status!r} \n\t\t\t\t\tErrors counted while handling data: {errors:d} ")

            except KeyError as e:
                errors += 1
                logger.exception(f"Error processing Telegram data. \n\t\t\t\t\tErrors counted while handling data: {errors:d} \n {e} ") #logs trace

        except (KeyboardInterrupt, SystemExit) as e:
            logger.info(f"Exiting via KeyboardInterrupt/SystemExit. \n\t\t\t\t\tErrors counted while handling data: {errors:d} \n") #logs trace
            poll(TOKEN, offset) #poll with higher offset so as to "Confirm messages", then EXIT
            # logger.exception(f"If stuck show traceback: {e}")
            if logger.getEffectiveLevel() <= 10: #Just trying to mimic logger.exception without "inspect" nor "linecache.py" modules
                print(f"Traceback: {'-'*100} ")
                print(f"Trace obj: {e.__traceback__} - Cause: {e.__cause__} - Context: {e.__context__}")
                trace = e.__traceback__
                while trace:
                    file = trace.tb_frame.f_code.co_filename.replace("\\","/") if os.name == 'nt' else trace.tb_frame.f_code.co_filename
                    print(f"In File: {file} - On Line number: {trace.tb_lineno}  ")
                    with open(file, "rt") as f:  #"r" - Read "t" - Text 
                        for i in range(trace.tb_lineno): 
                            source_line = f.readline() #single string
                    print(f"\t Source Line: {source_line.strip()}")
                    trace = trace.tb_next
            sys.exit(0)

        except Exception as e:
            logger.exception(f"Unexpected ERROR processing Telegram data: {e}")
            sys.exit(1)
        
    logger.critical(f"Exiting bot due to too many errors: {errors}")