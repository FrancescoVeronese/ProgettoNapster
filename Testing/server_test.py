#AREA DI TESTING PER LE SINGOLE FUNZIONALITA---server
#TESTING 1: LOGI

import socket
from random import *

#CON PYTHON 3.10 SONO STATI INSERITI I "MATCH" COME GLI SWITCH

def acceptLogin():
    # Quando si accetta, bisogna prendere la porta del client da dove altri peer prenderanno i file
    alphabet="abcdefghijklmnopqrstuvwxyz"
    sessionID=""
    valid=False
    while(valid==False):
        #generare una stringa di 16 caratteri con valori alfanumerici
        for x in range(0,16):
            choosetype=randint(0,1)
            if(choosetype==0):
                numberchooser=randint(0,9)
                sessionID=sessionID+str(numberchooser)
            else:
                charchooser=randint(0,25)
                sizechooser=randint(0,1)
                if(sizechooser==0):
                    sessionID=sessionID+alphabet[charchooser]
                else:
                    sessionID=sessionID+alphabet[charchooser].upper()
        
        #una volta creato il sessionID si controlla con una query al DB (tabella utenti),
        # nel caso vi sia già un peer connesso con quel sessionID (valid=false),
        # in tal caso si ricrea l'ID e si ritenta il controllo, se poi
        #si crea un ID non presente nel DB allora valid=true e si esce dal while
        valid=True
    response="ALGI"+sessionID
    return response

s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.setsockopt(socket.SOL_SOCKET,socket.SO_REUSEADDR,1)
s.bind(("",80))
s.listen(10)
CommandAction=""
response=""
while True:
    conn,addr=s.accept()
    packet=conn.recv(1024).decode()
    
    #si prendono i primi 4 byte(caratteri) della stringa inviata dal client, che identificano il tipo di comando inviato
    commandAction=packet[0:4]

    match commandAction:
        case 'LOGI' : 
            response=acceptLogin()
            conn.send(response.encode()) #manda al client una stringa di 20 byte al peer 4 cmd, 16 SID #X