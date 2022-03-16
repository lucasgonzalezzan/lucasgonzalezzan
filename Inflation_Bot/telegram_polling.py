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
        print("An exception occurred in urlopen telegram_polling", flush=True)  
        return "An exception occurred in urlopen telegram_polling", e.code
    except Exception as e:
        return "An exception occurred in urlopen telegram_polling", 404        

    else: return j, response.status

    

if __name__ == '__main__': #for testing
    import sys
    token = sys.argv[1] if len(sys.argv) > 2 else exit(1) 
    offset = sys.argv[2] if len(sys.argv) > 2 else exit(1) 

    url = 'https://api.telegram.org/bot' + str(token) + '/getUpdates?offset=' + str(offset)
    print(url, flush=True)
    httprequest = Request(url, headers={"Accept": "application/json"})

    for _ in range(20):
        r = poll(token, offset)
        print(r) #({'ok': True, 'result': []}, 200) or ('An exception occurred in urlopen polling', 409)
        try:
            with urlopen(httprequest) as response:
                print(response.status, flush=True, end="")
                print(response.read().decode(), flush=True) 

        except urllib.error.HTTPError as e:
            print(f"Aja! catched an urllib error: {e!r}")
            print(f"urllib error CODE: {e.code!r} {type(e.code)!r}")
#When  2 bots running:
#HTTPResponse object: <http.client.HTTPResponse object at 0x000001BC13EE0AF0> 200{"ok":true,"result":[]}
# Aja! catched an urllib error: <HTTPError 409: 'Conflict'>
# urllib error CODE: 409 <class 'int'>
    exit(0)