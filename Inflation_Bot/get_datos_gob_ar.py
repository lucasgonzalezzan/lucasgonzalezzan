from urllib.request import urlopen, Request
import urllib.error
import json

def ipc_poll(fecha, representacion = 'percent_change'):

    url = ('http://apis.datos.gob.ar/series/api/series/?' 
        + 'ids=148.3_INIVELNAL_DICI_M_26&start_date=' + str(fecha) 
        + '&representation_mode=' + str(representacion) ) #Inflacion IPC nacional como variacion mensual
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

# https://apis.datos.gob.ar/series/api/series?start_date=2018-08&ids=168.1_T_CAMBIOR_D_0_0_26
# {'data': [['2018-08-01', 27.525],
#   ['2018-08-02', 27.45],
#   ['2018-08-03', 27.29],...