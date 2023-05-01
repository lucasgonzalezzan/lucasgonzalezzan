from urllib.request import urlopen, Request 
from urllib.parse import quote, urlencode 
import urllib.error
import json

    

def push(token, chat_id, msg, keyboard = "", MarkdownV2 = False):

    if keyboard == "": pass
    else:
        if type(keyboard) != dict: return "keyboard must be a dictionary with buttons inside rows inside columns"
        keyboard = json.dumps(keyboard) 
        keyboard = "&reply_markup=" + quote(keyboard) #percent-encoding
    
    url = 'https://api.telegram.org/bot' + str(token) + '/sendMessage?' + urlencode({'chat_id': str(chat_id), 'text': str(msg)}) + keyboard
    if MarkdownV2: url = url + "&parse_mode=MarkdownV2" #Careful telegram MarkdownV2 specialch = "*[]()~>#+-=|.!"

    httprequest = Request(url, headers={"Accept": "application/json"}) 

    try:
        with urlopen(httprequest, timeout=5) as response:
            r = response.read().decode() 
    except urllib.error.HTTPError as e:
        print(f"An exception occurred in urlopen telegram_pushing: {e}", flush=True)  
        return e.code
    except Exception as e:
        print(f"An exception occurred in urlopen telegram_pushing: {e}", flush=True) 
        return 404

    else: return response.status


def form_data_headers(name, filename, data:bytes, mime, boundary = None) -> (bytes, "build multipart/form-data headers"):
    """Build the multipart/form-data headers to send POST with data file. Output as bytes for urlopen data"""
    boundary = boundary or "bHVjYXNnb256YWxlenphbg"
    headers = {"Content-Type" : f"multipart/form-data; boundary={boundary!s}"}
    body = bytes()

    #https://www.w3.org/Protocols/rfc1341/7_2_Multipart.html = "Note that the encapsulation boundary must occur at the beginning of a line, i.e., following a CRLF, and that that initial CRLF is considered to be part of the encapsulation boundary rather than part of the preceding part. The boundary must be followed immediately either by another CRLF and the header fields for the next part, or by two CRLFs, in which case there are no header fields for the next part (and it is therefore assumed to be of Content-Type text/plain)."
    form = (f"This is the preamble. To be ignored. \r\n"    #Python strings will automatically concatenate when not separated by a comma
            f"--{boundary}\r\n"         #the standard requires the boundary to start with two dashes -- (RFC 7578)
            f'Content-Disposition: form-data; name={name}; filename={filename}\r\n'
            f'Content-Type: {mime}\r\n\r\n') #MUST have 2 line separation then data
    body += form.encode(encoding = 'ascii', errors = 'strict')
    body += data
    body += bytes(f"\r\n--{boundary}--", encoding = 'ascii', errors = 'strict') #MUST have trail --

    return headers, body

def push_voice(token, chat_id, msg, file):
    url = 'https://api.telegram.org/bot' + str(token) + '/sendVoice?' + urlencode({'chat_id': str(chat_id), 'caption': str(msg)})
    headers, body = form_data_headers("voice", "join_ogg.ogg", file, "audio/vorbis")
    httprequest = Request(url, headers = headers, data = body) #This class is an abstraction of a URL request
    #con data=None --> GET, con data --> POST    
    # print(f"Full ulr: {httprequest.get_full_url()}\nHTTP method: {httprequest.get_method()} Data len: {len(httprequest.data)} Host: {httprequest.host}\nHeaders: {httprequest.header_items()}")
    try:
        with urlopen(httprequest) as response: 
            r = response.read().decode() #decode xq son bytes
    except urllib.error.HTTPError as e:
        print(f"An exception occurred in urlopen telegram_pushing: {e}", flush=True)  
        return e.code
    except Exception as e:
        print(f"An exception occurred in urlopen telegram_pushing: {e}", flush=True) 
        return 404

    else: return response.status

def push_photo(token, chat_id, msg, file):
    url = 'https://api.telegram.org/bot' + str(token) + '/sendPhoto?' + urlencode({'chat_id': str(chat_id), 'caption': str(msg)})
    headers, body = form_data_headers("photo", "join_ogg.ogg", file, "image/jpeg")
    httprequest = Request(url, headers = headers, data = body) #This class is an abstraction of a URL request
    #con data=None --> GET, con data --> POST    
    # print(f"Full ulr: {httprequest.get_full_url()}\nHTTP method: {httprequest.get_method()} Data len: {len(httprequest.data)} Host: {httprequest.host}\nHeaders: {httprequest.header_items()}")
    try:
        with urlopen(httprequest) as response: 
            r = response.read().decode() #decode xq son bytes
    except urllib.error.HTTPError as e:
        print(f"An exception occurred in urlopen telegram_pushing: {e}", flush=True)  
        return e.code
    except Exception as e:
        print(f"An exception occurred in urlopen telegram_pushing: {e}", flush=True) 
        return 404

    else: return response.status    
