from .mycrclib import crc32ogg16 as crc32


class ReverseBytes: #deal with bytes and LSB order in OGG

    def __set_name__(self, owner, name):    #define var name by instance
        self.private_name = '_' + name 

    def __get__(self, obj, objtype=None):   #get priv var as int
        value = getattr(obj, self.private_name)[::-1]       #ogg puts 1st LSB...MSByte last "https://xiph.org/vorbis/doc/framing.html"
        return int.from_bytes(value, byteorder='big', signed=False)     

    def __set__(self, obj, value):          #set priv var from int to bytes (number of bytes as defined in __init__)
        lenght = len(getattr(obj, self.private_name))       #original length stored in _name
        value = value.to_bytes(lenght, byteorder='big', signed=False)[::-1]     #ogg puts 1st LSB...MSByte last
        setattr(obj, self.private_name, value)

class OggPage:

    #public attribute: presented as int numbers so byte logic is done internally in the class
    version = ReverseBytes()
    headtype = ReverseBytes()
    granule = ReverseBytes()
    serial = ReverseBytes()
    sequence = ReverseBytes()
    checksum = ReverseBytes()
    segments = ReverseBytes()
    segtable = ReverseBytes()
    payload = ReverseBytes()

    def __init__(self, bytestream):

        self._tot_len = len(bytestream)

        #page header
        self._pattern = bytestream[0:4]
        self._version = bytestream[4:5]
        self._headtype = bytestream[5:6]
        self._granule  = bytestream[6:14]
        self._serial   = bytestream[14:18]
        self._sequence = bytestream[18:22]
        self._checksum = bytestream[22:26]
        self._segments = bytestream[26:27]
        self._segtable = bytestream[27:27+int.from_bytes(self._segments, 'big')]
        #rest of page payload
        self._payload = bytestream[27+int.from_bytes(self._segments, 'big'):]

    @property   #get raw bytes in private variables
    def raw(self):
        return self._pattern + self._version + self._headtype + self._granule + self._serial + self._sequence + self._checksum + self._segments + self._segtable + self._payload

    @property   #same as raw but recalc chechsum after all modifications
    def page(self): #recalc checksum before returning page bytestream
        self.checksum = crc32(self._pattern + self._version + self._headtype + self._granule + self._serial + self._sequence + bytes(4) + self._segments + self._segtable + self._payload)
        return self.raw


    @property   #lenght of bytestream
    def len(self):
        return len(self.raw)

    def __str__(self):  #__str__ representation of pages (byte fields)
        return (f"\nself._id = {id(self):#x}" 
                f"\nself._pattern  = {int.from_bytes(self._pattern, 'big'):#04x}" 
                f"\nself._version  = {int.from_bytes(self._version, 'big'):#04x}" 
                f"\nself._headtype = {int.from_bytes(self._headtype, 'big'):#04x}" 
                f"\nself._granule  = {int.from_bytes(self._granule, 'big'):#04x}" 
                f"\nself._serial   = {int.from_bytes(self._serial, 'big'):#04x}" 
                f"\nself._sequence = {int.from_bytes(self._sequence, 'big'):#04x}" 
                f"\nself._checksum = {int.from_bytes(self._checksum, 'big'):#04x}" 
                f"\nself._segments = {int.from_bytes(self._segments, 'big'):#04x}" 
                f"\nself._segtable = {int.from_bytes(self._segtable, 'big'):#04x}" 
                f"\nself._payload  = {int.from_bytes(self._payload[:16], 'big'):#04x}..."   )
    def __len__(self):  #same as >>m.len but now can >>len(m)
        return len(self.raw)
    

    #Page methods:
    def SetHead(self):
        self.headtype |= 0x02 #set = first page of logical bitstream (bos)
    def ClrHead(self):
        self.headtype &= 0xFD #unset = not first page of logical bitstream
    def SetTail(self):
        self.headtype |= 0x04 #set = last page of logical bitstream (eos)
    def ClrTail(self):
        self.headtype &= 0xFB #unset = not first page of logical bitstream
    def ClrHT(self):
        self.headtype &= 0xF9 #unset Head and Tails flags


class Ogg:

    def __init__(self, bytestream):
        if b'OggS' not in bytestream: raise ValueError("Error: No OggS identifier in file")

        self.__tot_len = len(bytestream)

        # paging
        self.__pages = list() 
        start = 0
        while (start is not None):
            end = bytestream.find(b'OggS', start+1) #when not found, end = -1
            if end == -1: end = None #[start:] to the end
            self.__pages.append( OggPage(bytestream[start:end]) ) #retrieve 'start' to byte before 'end'
            start = end

        if bytestream.count(b'OggS') != len(self.__pages): raise ValueError("Error processing OggS identifiers in file")

    #Each ogg page is an object, all grouped in a list
    @property
    def pages(self):    #return a list of objects, for debug etc
        return self.__pages

    @pages.setter   #when adding new page, look for OggS in order to build page object structure
    def pages(self, bytestream): #append new OggPages objects
        if b'OggS' not in bytestream: raise ValueError("Error: No OggS identifier in file")
        # paging
        #self.__pages = list() page already initialized 
        init_len = len(self.__pages)
        start = 0
        while (start is not None):
            end = bytestream.find(b'OggS', start+1) #when not found, end = -1
            if end == -1: end = None #[start:] to the end
            self.__pages.append( OggPage(bytestream[start:end]) ) #new OggPages instance
            start = end

        if bytestream.count(b'OggS') + init_len != len(self.__pages): raise ValueError("Error processing OggS identifiers in file")

    def AddOggPage(self, obj): #Add a shallow-copy of the obj
        self.__pages.append(obj)

    @property   #return total byte lenght (sume of pages lenghts), called as m.len
    def len(self):
        l = 0 
        for p in self.__pages:
            l += p.len
        return l

    @property   #return valid Ogg file (like raw but recalc checksum after modifications)
    def ogg(self):
        bytestream = b''
        for p in self.__pages:
            bytestream += p.page
        return bytestream

    @property   #return current bytestram as is
    def raw(self):
        bytestream = b''
        for p in self.__pages:
            bytestream += p.raw
        return bytestream        
    
    @property   #return 1st and 2nd pages (codec info)
    def head(self):
        bytestream = b''
        for p in self.__pages[0:2]:
            bytestream += p.page
        return bytestream

    @property   #return all but 1st and 2nd pages
    def tail(self):
        bytestream = b''
        for p in self.__pages[2:]:
            bytestream += p.page
        return bytestream

    #OGG methods:
    def __str__(self):  #when printing return ID and __str__ representation of pages (byte fields)
        s = f"\nself.id = {id(self):#x} \n__pages: "
        for i, p in enumerate(self.__pages):
            s += "\n\tPage" + str(i) + ": " + p.__str__()
        return s

    def __len__(self):  #same as >>m.len but now can >>len(m)
        return len(self.raw)

    def __eq__(self, other): 
        return self.raw == other.raw

    def __lt__(self, other): #>>> a<b --> True
        return len(self) < len(other)

    def __add__(self, other):   
        return self.raw + other.tail


    def SetHead(self):
        self.__pages[0].SetHead()
    def SetTail(self):
        self.__pages[-1].SetTail()  
    def ClrHT(self):    #clear all pages H&T flags
        for p in self.__pages:
            p.ClrHT()
    def SetHT(self):    #set head an tail on 1st and last pages
        self.SetHead()
        self.SetTail()

    #to avoid gaps in the audio the "granules" must be consecutive and equal to number of audio-samples decoded "https://xiph.org/vorbis/doc/framing.html"
    def GetGranules(self):  #get a list of granule field on every page
        g = list()
        for p in self.__pages:
            g.append(p.granule)
        return g     
    def GetLastGranule(self):   
        return self.__pages[-1].granule
    def SetGranules(self, offset):  #adjust granules by and offset (i.e. last granule of previous file)
        found_last = False
        for p in self.__pages:
            if found_last: p.granule += offset      #second, add offset value to every page in the added stream
            if p.granule >= offset: found_last = True   #first, find highest granule (by offset)
    def ClrGranules(self):
        for p in self.__pages:
            p.granule = 0

    def GetSerials(self):
        g = list()
        for p in self.__pages:
            g.append(p.serial)
        return g     
    def SetSerials(self, value): 
        for p in self.__pages:
            p.serial = value

    def GetSequence(self):  #Page counter; lets us know if a page is lost (useful where packets span page boundaries). Not mandatory
        g = list()
        for p in self.__pages:
            g.append(p.sequence)
        return g     
    def SetSequence(self): #page sequence (inc by 1 on every page from zero)
        for i, p in enumerate(self.__pages):
            p.sequence = i



def join_ogg(audios:"list(Ogg)" = [None]) -> object:
    """ Join list of Ogg objects assuming same codec Vorbis"""
    if not all([isinstance(a, Ogg) for a in audios]): raise TypeError("Not a list of OGGs")
    mix = Ogg(audios[0].head)
    mix.ClrGranules()
    for obj in audios:
        offset = mix.GetLastGranule() #get last granule before every join ("total samples encoded after including all packets finished on this page")
        mix.pages = obj.tail #append new OggPages objects, whithout the 1st and 2nd pages of files
        mix.SetGranules(offset) #will find offset in Ogg and, on next OggPages, increase granule of pages by offset

    mix.SetSerials(int.from_bytes(b'OGUT', 'big')) #set same serial for all ("serial number is the means by which pages physical pages are associated with a particular logical stream")
    mix.ClrHT() #clear head and tail tag on all pages
    mix.SetHT() #set head an tail on 1st and last pages
    mix.SetSequence() #this is optional

    return mix
