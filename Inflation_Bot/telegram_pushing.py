from urllib.request import urlopen, Request #in Python3 urllib was split
from urllib.parse import quote, urlencode #to skip forbidden ch in url
import urllib.error
import json

def push(token, chat_id, msg, keyboard = "", MarkdownV2 = False):

    if keyboard == "": pass
    else:
        if type(keyboard) != dict: return "keyboard must be a dictionary with buttons inside rows inside columns"
        keyboard = json.dumps(keyboard) #turn dict to string
        keyboard = "&reply_markup=" + quote(keyboard) # then percent-encoding
    
    url = 'https://api.telegram.org/bot' + str(token) + '/sendMessage?' + urlencode({'chat_id': str(chat_id), 'text': str(msg)}) + keyboard
    if MarkdownV2: url = url + "&parse_mode=MarkdownV2" #Careful telegram MarkdownV2 specialch = "*[]()~>#+-=|.!"

    httprequest = Request(url, headers={"Accept": "application/json"}) #This class is an abstraction of a URL request

    try:
        with urlopen(httprequest) as response:
            r = response.read().decode() 
    except urllib.error.HTTPError as e:
        print("An exception occurred in urlopen telegram_pushing", flush=True)  
        return e.code
    except Exception as e:
        return 404

    else: return response.status