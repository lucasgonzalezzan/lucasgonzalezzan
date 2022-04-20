from .crc_tables import crc32_table, crc32_table_16bit
mask_crc32 = 0x104C11DB7 #normal representation Technically, the CRC 32-bit constant 0x04C11DB7 is really a 33-bit constant 0x104C11DB7 which is classified as an IEEE-802 CRC. See RFC 3385
mask_crc32_rev = 0xEDB88320 # lsbit-first (reversed) CRC32 polynomial of 0xEDB88320 can also be written msbit-first (normal) as 0x04C11DB7


def crc32ogg(msg:bytes) -> (int, "OGG crc as int, Ogg class handles the byte conversion"):
    """ calc crc32 with ogg checksum parameters """
    return crc32calc_tablelookup(msg, 0, False, False, False)

#idem as crc32ogg but using 16bit table for lookup
def crc32ogg16(msg:bytes) -> (int, "OGG crc as int, Ogg class handles the byte conversion"):
    """ calc crc32 with ogg checksum parameters """
    return crc32calc_tablelookup_16bit(msg, 0, False, False, False)    

def crc32calc_tablelookup(msg:bytes, init=0x0, refin=False, refout=False, xorout=False) -> (bytes, "CRC32 in bytes calc from crc32_table"): #.__annotations__
    """ calc crc32 from pre computed table """  #.__doc__
    crc = init
    for b in msg:
        if refin: b = int('{:08b}'.format(b)[::-1], base=2) #input bit reflected        
        crc ^= b << 24 #add previuos crc
        crc = crc32_table[crc & 0xff000000] ^ ((crc & 0x00ffffff) << 8) 
    if refout: crc = int('{:032b}'.format(crc)[::-1], base=2) #crc bit reflected
    if xorout: return crc ^ 0xffffffff 
    else: return crc 

#for a 6MByte stream around 0.2 seg faster, not a lot
def crc32calc_tablelookup_16bit(msg:bytes, init=0x0, refin=False, refout=False, xorout=False) -> bytes:
    """ calc crc32 from pre computed table 2 bytes at a time """  #.__doc__
    crc = init
    for i in range( (len(msg)+1) // 2): 
        try:
            b = (msg[i*2] << 8) + msg[i*2+1] # (0,1), (2,3), (4,5) ...
            if refin: b = int('{:08b}'.format(msg[i*2])[::-1] + '{:08b}'.format(msg[i*2+1])[::-1], base=2) #input bit reflected   
        except IndexError:  #if not a pair number of bytes
            b = msg[-1]    
            if refin: b = int('{:08b}'.format(b)[::-1], base=2) 
            crc ^= b << 24 
            crc = crc32_table_16bit[(crc >> 8) & 0x00ff0000] ^ ((crc & 0x00ffffff) << 8)  
            break
        crc ^= b << 16 #add previuos crc
        crc = crc32_table_16bit[crc & 0xffff0000] ^ ((crc & 0x0000ffff) << 16) 
    if refout: crc = int('{:032b}'.format(crc)[::-1], base=2) #crc bit reflected
    if xorout: return crc ^ 0xffffffff
    return crc

  
#func to build crc pre computed table 2 of 2 steps
def format_crc_table(key:"list(int)", value:"list(int)", hexadecimal : "F for hex, True for int" = False) -> (str, "takes key list and crc list and format a dict as text, 4 pairs each row"):
    text = "crc32_table = { "
    for i in range(len(key)):
        if i%4 == 0: text += '\n'
        if hexadecimal: 
            k = f"{key[i]:#010x}"
            v = f"{value[i]:#010x}"
        else: 
            k = f"{key[i]:10d}" 
            v = f"{value[i]:10d}"
        text += k + " : " + v 
        text += " , " if i < len(key)-1  else " } "
    return text

#To save the table to crc_tables.py
# >>> k,v = make_crc32_table_16bit()
# >>> text = format_crc_table(k,v,True)
# >>> with open("16bit.txt", 'w') as f:
# ...  f.write(text)

#func to build crc pre computed table 1 of 2 steps
def make_crc32_table(poly=0x104C11DB7) -> (list, list,"build crc32 table, 256 keys and crc 32bit long"): 
    crc32_list = list()
    key_bytes = list()
    for crc in range(0, 2**32, 2**24):        
        key_bytes.append(crc)   #save key of table
        for i in range(8):
            crc = crc << 1
            if crc & 0x100000000: crc ^= poly 
        crc32_list.append(crc)
    return  key_bytes, crc32_list

def make_crc32_table_16bit(poly=0x104C11DB7) -> (list, list,"build crc32 table, 65536 keys and crc 32bit long"): 
    crc32_list = list()
    key_bytes = list()
    for crc in range(0, 2**32, 2**16):        
        key_bytes.append(crc)   #save key of table
        for i in range(16):
            crc = crc << 1
            if crc & 0x100000000: crc ^= poly 
        crc32_list.append(crc)
    return  key_bytes, crc32_list


# RefIn = mirror bits in every byte (for Ethernet LSBit first, byte order not changed)
# RefOut = mirror bits in crc
def crc32calc(msg, init=0xffffffff, refin=False, refout=False, xorout=False):
    crc = init
    for b in msg:
        if refin: b = int('{:08b}'.format(b)[::-1], base=2) #byte bit reflected
        crc ^= b << 24
        for i in range(8):
            crc = (crc << 1) ^ 0x04C11DB7 if crc & 0x80000000 else crc << 1
    crc &= 0xffffffff   #needs & mask xq ignores bit #33 when Xoring
    if refout: crc = int('{:032b}'.format(crc)[::-1], base=2) #crc bit reflected, fill '0' until 32 ch
    if xorout: return crc ^ 0xffffffff 
    else: return crc

#another way to calc the same but in reverse i.e. shifht right & check bit 0
def crc32calc_r(msg, init=0xffffffff): 
    crc = init
    for b in msg:
        crc ^= b 
        for i in range(8):
            crc = (crc >> 1) ^ 0xEDB88320 if crc & 0x1 else crc >> 1 #0x04C11DB7 bits reflected
    return crc & 0xffffffff    


if __name__ == '__main__':

    import functools
    import time
    def timer(func):
        """print the runtime of the decorated function"""
        @functools.wraps(func)
        def wrapper_timer(*args, **kwargs):
            start_time = time.perf_counter()    #1
            value = func(*args, **kwargs)
            end_time = time.perf_counter()      #2
            run_time = end_time - start_time    #3
            print(f"finished {func.__name__!r} in {run_time:.4f} secs") 
            return value
        return wrapper_timer

    @timer
    def waste_some_time(num_times):
        for _ in range(num_times):
            sum([i**2 for i in range(10000)])


    string = input("Comma separated bytes (7f, ca, fe, 42): ")
    string = [x.strip() for x in string.split(',')] 
    number = [int(x, base=16) for x in string] 
    bytestream = bytes(number)

    print("\n\nFile in HEX: ", end='')
    for b in bytestream:    print(f"{b:02X} ", end='' )
    else: print()

    print(f"CRC32_FF/MPEG-2:                {crc32calc(bytestream):08X}") 
    print(f"CRC32_FF/BZIP2 XOR invertido:   {crc32calc(bytestream) ^ 0xffffffff :08X}")
    print(f"CRC32_0/OGG:                    {crc32calc(bytestream, 0):08X}") 
    print(f"CRC32_0/POSIX XOR invertido:    {crc32calc(bytestream, 0) ^ 0xffffffff :08X}")
    print(f"IDEM w/rev calc crc32calc_r:    {crc32calc_r(bytestream, 0) ^ 0xffffffff :08X}")

    print(f"CRC32_FF/Ethernet:              {crc32calc(bytestream, 0xffffffff, True, True, True) :08X}")

    print(f"CRC32 OGG-header  (8bit table): {crc32ogg(bytestream):08X}")
    print(f"CRC32 OGG-header (16bit table): {crc32ogg16(bytestream):08X}")


# https://crccalc.com/ pagina calculos:
    # Algorithm     Result      Check       Poly        Init        RefIn   RefOut  XorOut
    # CRC-32/MPEG-2 0x047679CA  0x0376E6E7  0x04C11DB7  0xFFFFFFFF  false   false   0x00000000
    # CRC-32/BZIP2  0xFB898635  0xFC891918  0x04C11DB7  0xFFFFFFFF  false   false   0xFFFFFFFF
    # CRC-32 OGG      04C11DB7              0x04C11DB7  0x00000000  false   false   0x00000000 (OJO! LSByte fist in .ogg page header)
    # CRC-32/POSIX  0xFB3EE248  0x765E7680  0x04C11DB7  0x00000000  false   false   0xFFFFFFFF
    # CRC-32 (Ethe) 0x36DE2269  0xCBF43926  0x04C11DB7  0xFFFFFFFF  true    true    0xFFFFFFFF