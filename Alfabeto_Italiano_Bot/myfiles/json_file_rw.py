import json

def wrapp_JSONErrors(func):
    def inner(f, *args):
        try:
            return func(f, *args)
        except json.decoder.JSONDecodeError as e:
            raise FileNotFoundError(f"JSONDecodeError from {__name__} \nJSONDecodeError: {e}") from None
    return inner


@wrapp_JSONErrors
def json_read(file):
    return json.loads(file_read(file))

@wrapp_JSONErrors
def json_write(file, txt):
    return file_write(file, json.dumps(txt, indent=4)) 

#write as stream of bytes
def bin_read(file):
    with open(file, "rb", buffering=0) as f:  #"r" - Read "b" - binary mode
        return f.read()
        
def bin_write(file, bin):
    with open(file, "wb", buffering=0) as f:  
        return f.write(bin)        
        
def bin_append(file, bin):
    with open(file, "ab", buffering=0) as f:  
        return f.write(bin)        

#read/write as text        
def file_lines(file):
    with open(file, "rt") as f:  #"r" - Read "t" - Text 
        return f.readlines()#returns a list containing each line in the file
    
def file_read(file):
    with open(file, "rt") as f:  #"r" - Read "t" - Text 
        return f.read() #returns the specified number of bytes from the file. Default is -1
    
def file_print(file):    
    f = open(file,"r") 
    lines = f.readlines() #or readline(s) for 1 line, returns a list containing each line in the file
    for line in lines:
        print(line, end="", flush=True)
    f.close()
    
def file_append(file, txt):
    with open(file, "a", newline='\n') as f: #"a" - Append - will append to the end of the file "w" - Write - will overwrite any existing content
        return f.write(str(txt))

def file_write(file, txt):
    with open(file, "w", newline='\n') as f: #"a" - Append - will append to the end of the file "w" - Write - will overwrite any existing content
        return f.write(str(txt))
        
def file_delete(file):
    if os.path.exists(file):
      os.remove(file)
    else:
      print("The file does not exist")
