import socket
from random import *

#CON PYTHON 3.10 SONO STATI INSERITI I "MATCH" COME GLI SWITCH

def acceptLogin():
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
    

def acceptAdd(packet):
    #qui il server riceverà il file e lo salverà in una directory specifica

    #riceve cmd 4byte, sID 16byte, MD5 32byte,nome file 100byte
    sID=packet[4:20]
    MD5=packet[20:52]
    fileName=packet[52:152]

    #si aggiunge: nome file, MD5, numero versione (autoincrementante), session ID nel DB (tabella file)
    #il sessionID presente come chiave esterna serve per eliminare tutti i file presenti nel DB appartenenti a un utente
    #non più connesso
    
    directory="" #3B

    #Per inviare al client il numero di file uguali contenuti nel server nella directory dove sono ospitati
    #si effettua una query SELECT COUNT DISTINCT in base all'MD5
    response="AADD"+directory
    
    return response

def acceptRemove(packet):
    sID=packet[4:20]
    MD5=packet[20:52]
    #rimuove dalla cartella di salvataggio il file
    #rimuove dalla tabella file, i record che hanno session id=sID e MD5=MD5
    directory="" #3B
    response="ADEL"+directory
    return response
    
def findFile(packet):
    sID=packet[4:20]

    #manderà al peer numero di file con MD5 uguale
    #riporterà 
    numfile=0
    #invia al peer gli MD5 dei file con nome file che comprende il nome inviato dal peer stesso
    response=""
    return response

def acceptLogout(packet):
    sID=packet[4:20]
    #ELIMINA file dalla directory
    #query SQL che conta i file presenti nel DB con quel sID e li elimina
    numfile=0
    response="ALGO"+str(numfile)
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
        case 'ADDF':
            response=acceptAdd(packet)
            conn.send(response.encode()) #risponde con la conferma dell'inserimento nel DB del file,
                        # e del numero di file con stesso MD5 preesnti
        case 'DELF':
            response=acceptRemove(packet)
            conn.send(response.encode()) #risponde con la conferma della cancellazione del file
        case 'FIND':
            response=findFile()
            conn.send(response.encode())
        case 'LOGO':
            response=acceptLogout()
            conn.send(response.encode())