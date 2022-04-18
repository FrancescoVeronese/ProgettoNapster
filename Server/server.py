import socket
from random import *
import sys
import mysql.connector
from requests import Session 
#ERRORE RIGA 33 "unknown column in 'Field List'"

def dataSender(send):
    conn.send(str(send).encode())
def acceptLogin():
   
    IPAddress=packet[4:15]
    Port=packet[15:20]
    
    alphabet="abcdefghijklmnopqrstuvwxyz"
    sessionID="" 
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
    print(f"IL SID GENERATO è {sessionID}\n")
    try:
        valori=(sessionID,IPAddress,Port)
        cursor.execute(f"INSERT INTO UTENTE(SID,IP,PORT) VALUES (%s,%s,%s)",valori)
        mydb.commit()
    except BaseException as errore: #Tutte le eccezioni ereditano da Baseexception
        print("ERRORE:"+errore.msg)
        sessionID="0000000000000000"    
        ''' Al posto di cercare il numero di utenti con quel SID o altro, il metodo pià semplice è lasciare un
        eccezione, che se trovata, ritorna tutti zero al client
        try:
            cursor.execute(f"SELECT COUNT(*) FROM UTENTE WHERE SID='{sessionID}'") 
            queryresult=cursor.fetchall()[0][0]
            print(f"Il SID creato è presente nel DB {queryresult} volte")
            if(int(queryresult)==0):
                print(f"Il SID non è presente nel DB, invio del SID al client...\n")
                valid=True
                valori=(sessionID,IPAddress,Port)
                cursor.execute("INSERT INTO UTENTE (SID,IP,PORT) VALUES (%s,%s,%s)",valori)
                mydb.commit()
            else:
                print(f"SID già presente nel DB, generazione di un altro SID...\n")       
        except:
            print("ERRORE CONTROLLO/INSERIMENTO SID NEL DATABASE")
            sessionID='0000000000000000' '''
        
    response="ALGI"+sessionID
    return response
    

def acceptAdd(packet):

    #riceve cmd 4byte, sID 16byte, MD5 32byte,nome file 100byte
    sID=packet[4:20]
    MD5=packet[20:52]
    fileName=packet[52:152]
    try:
        mydb=mysql.connector.connect(host="localhost",user="francesco",password="1",database="NAPSTERDB")
        cursor=mydb.cursor()
        cursor.execute("INSERT INTO FILE(MD5,NAME) VALUES(%s,%s)",MD5,fileName)
        mydb.commit()
        cursor.execute("INSERT INTO ARCHIVIO(SID_UTENTE,MD5_FILE) VALUES(%s,%s",sID,MD5)
        mydb.commit()
        print(f"File {fileName}, con MD5 {MD5} del peer {sID} inserito nel DB\n")
    except mysql.connector.Error as errore:
        print("ERRORE nell'aggiunta del file:"+errore.msg)
    
    cursor.execute("SELECT COUNT (SID) FROM ARCHIVIO WHERE MD5=%s",MD5) #si conta quante volte il file sia presente nel DB
    copy=cursor.fetchall()[0][0]
    copy=copy.ljust(3)
    #il sessionID presente come chiave esterna serve per eliminare tutti i file presenti nel DB appartenenti a un utente
    #non più connesso
    response="AADD"+copy
    
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
    search_string=packet[20:40]
    filename=packet[40:140]
    #manderà al peer numero di file con MD5 uguale
    #riporterà 
    numfile=0
    #invia al peer gli MD5 dei file con nome file che comprende il nome inviato dal peer stesso
    response=""
    return response

def acceptLogout(packet):
    sID=packet[4:20]
    #query SQL che conta i file presenti nel DB con quel sID e li elimina
    numfile=0
    response="ALGO"+str(numfile)
    return response
#connessione al database
try: 
    mydb=mysql.connector.connect(host="localhost",user="francesco",password="1",database='NAPSTERDB')
    cursor=mydb.cursor()
except:
    print("La connessione al Database non ha avuto successo")


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
    if(commandAction=='LOGI'):
            response=acceptLogin()
            print(f"La risposta al client è {response}")
            dataSender(response)#manda al client una stringa di 20 byte al peer 4 cmd, 16 SID #X
    else:
        if(commandAction=='ADDF'):
            response=acceptAdd(packet)
            print(f"La risposta al client è {response}")
            dataSender(response) #risponde con la conferma dell'inserimento nel DB del file,
            # e del numero di file con stesso MD5 preesnti
        else:
            if(commandAction=='DELF'):
                response=acceptRemove(packet)
                print(f"La risposta al client è {response}")
                dataSender(response) #risponde con la conferma della cancellazione del file
            else:
                if(commandAction=='FIND'):
                    response=findFile()
                    print(f"La risposta al client è {response}")
                    dataSender(response)
                else:
                    if(commandAction=='LOGO'):
                        response=acceptLogout()
                        print(f"La risposta al client è {response}")
                        dataSender(response)