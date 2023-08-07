from urllib.request import urlopen, Request
import urllib.error
import json

def ipc_poll(start_date, representation = 'percent_change'):

    url = ('http://apis.datos.gob.ar/series/api/series/?' 
        + 'ids=148.3_INIVELNAL_DICI_M_26&start_date=' + str(start_date) 
        + '&representation_mode=' + str(representation) ) #Inflation national IPC monthly 
    httprequest = Request(url, headers={"Accept": "application/json"})

    try:
        with urlopen(httprequest) as response: 
            r = response.read().decode() 
            j = json.loads(r) 

    except urllib.error.HTTPError as e:
        print("An exception occurred in urlopen IPCpolling get_datos_gob_ar",flush=True)  
        return "An exception occurred in urlopen IPCpolling get_datos_gob_ar", e.code
    except Exception as e:
        return "An exception occurred in urlopen IPCpolling get_datos_gob_ar", 404           

    else: return j['data'], response.status 
