import json

def wrapp_JSONErrors(func):
    def inner(f, *args):
        try:
            return func(f, *args)
        except json.decoder.JSONDecodeError as e:
            raise FileNotFoundError(e)
    return inner


@wrapp_JSONErrors
def json_read(file):
    return json.loads(file_read(file))

@wrapp_JSONErrors
def json_write(file, txt):
    return file_write(file, json.dumps(txt, indent=4)) #Pretty printing


def file_lines(file):
    #'with' automatically closes your file, no need for f.close()
    with open(file, "rt") as f:  #"r" - Read "t" - Text 
        return f.readlines()#returns a list containing each line in the file
    
def file_read(file):
    with open(file, "rt") as f:  #"r" - Read "t" - Text 
        return f.read() #single string
    
def file_print(file):    
    f = open(file,"r") 
    lines = f.readlines() #or readline(s) for 1 line, returns a list containing each line in the file
    for line in lines:
        print(line, end="", flush=True)
    f.close()
    
def file_append(file, txt):
    with open(file, "a") as f: #"a" - Append - will append to the end of the file "w" - Write - will overwrite any existing content
        return f.write(str(txt))

def file_write(file, txt):
    with open(file, "w") as f: #"a" - Append - will append to the end of the file "w" - Write - will overwrite any existing content
        return f.write(str(txt))
        
def file_delete(file):
    if os.path.exists(file):
      os.remove(file)
    else:
      print("The file does not exist")
