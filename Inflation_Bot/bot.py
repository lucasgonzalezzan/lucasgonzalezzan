#!/usr/bin/env python3
'''Bot to get inflation info from https://datos.gob.ar/


Usage:
    export token variables "TOKEN=1234567890:cmZoYW1sb3p0a3hudjF6endrMWt2a2p1cWx ; export TOKEN"
    python bot.py <offset>  #optionally to define last update

Author:
    Lucas Gonzalez Zan - 01.03.2022
'''

import logging
import logging.config
import os
import sys

from telegram_msg_process import data_handler as handler
from telegram_polling import poll as poll
from json_file_rw import json_read

import apidata  

print("Running: ", sys.argv[0], flush=True) #print name of script

# Enabling logging
try:
    LOGLVL = os.getenv("LOGLVL") 
    loglevels = ["NOTSET","DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
    if LOGLVL in loglevels: 
        logging.basicConfig(level=loglevels.index(LOGLVL)*10, #change to DEBUG/INFO/WARNING etc
                            format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
        logging.info("Loaded logging as defined in enviroment LOGLVL")        
    else:
        
        logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
        logging.info("Loaded logger from logging.conf")#qualname corresponds to the getLogger() call in our code


except:
    logging.basicConfig(level=logging.DEBUG, #change to DEBUG/INFO/WARNING etc
                        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    logging.info("Loaded logging from basicConfig")

logger = logging.getLogger() #root logger


#export TOKEN en bash, es para el bot
TOKEN = os.getenv("TOKEN")
if TOKEN is None or len(TOKEN) != 46: #10 numeros + ':'' + 35 ch
    logger.error("No TOKEN specified \n Try sth like 'TOKEN=1234567890:cmZoYW1sb3p0a3hudjF6endrMWt2a2p1cWx ; export TOKEN; and run again'")
    sys.exit(1)
logging.debug(f"TOKEN is set.") 
apidata.home = os.getcwd().replace("\\","/") #returns str pero en Win turn '\'' to linux 
logging.debug(f"Current directory = {apidata.home!r}") 

if __name__ == '__main__':
    logger.info("Starting bot.")
    logger.info("Loading JSON data from data/IPC.json")
    try: 
        apidata.ipc = json_read(apidata.home + "/data/IPC.json") 
    except FileNotFoundError:
        logger.exception("Failed to load JSON file.") #
    else:
        logger.info(f"Loaded local file data/IPC.json")
        logger.debug(f"Data: {apidata.ipc!r}")
    
    offset = sys.argv[1] if len(sys.argv) > 1 else 0 #ternary operator
    errors = 0
    while errors < 100:

        try: 
            payload, status = poll(TOKEN, offset) # get message updates from telegram server https://core.telegram.org/bots/api#getupdates
            if not(200 <= status < 300): 
                errors += 1
                logger.error(f"Polling returned status not 2XX: {status!r}")
                logger.error(f"Errors counted while handling data: {errors:d}")
                continue
        
            logger.debug(f"Payload is: {payload!r} Status is: {status!r}")
            
            if len(payload['result']): # json field with messages not null?
                if 'result' in payload: 
                    last_id = len(payload['result'])-1
                    if 'update_id' in payload['result'][last_id]:
                        offset = int(payload['result'][last_id]['update_id']) + 1 # Save message id. "An update is considered confirmed as soon as getUpdates is called with an offset higher than its update_id"
                        logger.info(f"Processing {len(payload['result']):d} menssages, last update_id was {offset-1:d}")
                        for index, msg in enumerate(payload['result']):
                            status = handler(TOKEN, msg) #returns response.status
                            logger.debug(f"telegram_msg_process import data_handler Status is: {status!r}")
                            if not(200 <= status < 300): 
                                errors += 1
                                logger.error(f"telegram_msg_process import data_handler returned: {status!r} \nErrors counted while handling data: {errors:d} ")
                    else: 
                        errors += 1
                        logger.error(f"Couldn't process message update_id: {payload!r} \nErrors counted while handling data: {errors:d} ")
                else: 
                    errors += 1
                    logger.error(f"Couldn't process message results: {payload!r} \nErrors counted while handling data: {errors:d} ")
            else: logger.info(f"No messages to process.")

        except (KeyboardInterrupt, SystemExit):
            logger.exception(f"Exiting via KeyboardInterrupt/SystemExit. \nErrors counted while handling data: {errors:d}") #logs trace
            sys.exit(0)
        except (ValueError, TypeError):
            errors += 1
            logger.exception(f"Error processing Telegram data. \nErrors counted while handling data: {errors:d} ") #logs trace
            continue   
        except Exception:
            logger.exception(f"Unexpected ERROR processing Telegram data.")
            sys.exit(1)
        

    logger.critical(f"Exiting bot due to too many errors: {errors}")
    exit(1)
