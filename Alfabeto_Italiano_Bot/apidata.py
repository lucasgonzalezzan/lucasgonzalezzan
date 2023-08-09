# tracking of users and their text given to spell out
users = dict()
class User:
        """user (chatid) data to service"""
        def __init__(self, last_cmd = None, words = None, chars = None, time = 0): 
                self.last_cmd = last_cmd
                self.words = words if words else list()
                self.chars = chars if chars else list()
                self.time = time


home = None
oggfiles = dict() #in memory audio files
abc_it = { 
        "A" : "Ancona" , 
        "B" : "Bologna" , 
        "C" : "Cagliari" , 
        "D" : "Domodossola" , 
        "E" : "Enna" , 
        "F" : "Firenze" , 
        "G" : "Genova" , 
        "H" : "Hotel" , 
        "I" : "Isernia" , 
        "J" : "Jeans" , 
        "K" : "Ketchup" , 
        "L" : "Livorno" , 
        "M" : "Milano" , 
        "N" : "Napoli" , 
        "O" : "Ostuni" , 
        "P" : "Palermo" , 
        "Q" : "Quarto" , 
        "R" : "Roma" , 
        "S" : "Sassari" , 
        "T" : "Torino" , 
        "U" : "Urbino" , 
        "V" : "Venezia" , 
        "W" : "Wurstel" , 
        "X" : "Xeno" , 
        "Y" : "Yogurth" , 
        "Z" : "Zagarolo"
        }