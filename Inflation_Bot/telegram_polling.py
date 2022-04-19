from urllib.request import urlopen, Request
import urllib.error
import json


def poll(token, offset = 0):
    url = 'https://api.telegram.org/bot' + str(token) + '/getUpdates?offset=' + str(offset)
    httprequest = Request(url, headers={"Accept": "application/json"})

    try: 
        with urlopen(httprequest) as response: 
            r = response.read().decode() 
            j = json.loads(r) 

    except urllib.error.HTTPError as e:
        print(f"An exception occurred in urlopen telegram_polling {e}", flush=True)  
        return "An exception occurred in urlopen telegram_polling", e.code
    except Exception as e:
        print(f"An exception occurred in urlopen telegram_polling {e}", flush=True)  
        return "An exception occurred in urlopen telegram_polling", 404        

    else: return j, response.status

