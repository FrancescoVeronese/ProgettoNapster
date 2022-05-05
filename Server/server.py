import ipaddress
import socket
from random import *
import sys
import mysql.connector
from requests import Session 



def dataSender(send):
    conn.send(str(send).encode())
def acceptLogin(): #OK
   
    IPAddress=packet[4:19]
    Port=packet[19:24]
    
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
        valori=(sessionID,str(IPAddress),str(Port))
        cursor=mydb.cursor()
        cursor.execute("INSERT INTO UTENTE(SID,IP,PORT) VALUES (%s,%s,%s)",valori)
        mydb.commit()
        print("Utente %s connesso, da porta %s\n",IPAddress,Port)
    except BaseException as errore: #Tutte le eccezioni ereditano da Baseexception
        print("ERRORE:"+errore.msg)
        sessionID="0000000000000000"
        
    response="ALGI"+sessionID
    return response
    

def acceptAdd(packet): #OK#
    #riceve cmd 4byte, sID 16byte, MD5 32byte,nome file 100byte
    sID=packet[4:20]
    MD5=packet[20:52]
    fileName=packet[52:152]
    try:
        mydb=mysql.connector.connect(host="localhost",user="francesco",password="1",database="NAPSTERDB")
        cursor=mydb.cursor()
        info=(MD5,fileName,sID)
        cursor.execute("INSERT INTO FILE(MD5,NOME,ID_UTENTE) VALUES(%s,%s,%s)",info)
        mydb.commit()
        print(f"Il File: {fileName}, con MD5 {MD5} del peer {sID} inserito nel DB\n")
    except mysql.connector.Error as errore:
        print("ERRORE nell'aggiunta del file:"+errore.msg)
    
    MD5tupla=(MD5,)
    cursor.execute("SELECT COUNT(*) FROM FILE WHERE MD5=%s",MD5tupla) #si conta quante volte il file sia presente nel DB
    copy=cursor.fetchall()
    copy=str(copy[0][0])
    #il sessionID presente come chiave esterna serve per eliminare tutti i file presenti nel DB appartenenti a un utente
    #non più connesso
    response="AADD"+copy
    return response

def acceptRemove(packet):#OK
    sID=packet[4:20]
    MD5=packet[20:52]

    removeinfo=(sID,MD5)
    try:
        cursor=mydb.cursor()
        cursor.execute("SELECT COUNT(*) FROM FILE WHERE ID_UTENTE=%s AND MD5=%s",removeinfo)
        deletedfiles=cursor.fetchall()
        directory=str(deletedfiles[0][0]).ljust(3)
    except BaseException as erro:
        print("Errore calcolo numero file cancellati: %s",erro.msg)

    try:
        cursor=mydb.cursor()
        cursor.execute("DELETE FROM FILE WHERE ID_UTENTE=%s AND MD5=%s",removeinfo)
        mydb.commit()
    except BaseException as err:
        print("Errore cancellazione file: %s",err.msg)
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

def acceptLogout(packet): #OK
    #Conta i file da eliminare dell'utente che fa logout
    #cancella i file dell'utente in questione
    #cancella l'utente dal DB
    sID=packet[4:20]
    filenum=0
    try:
        sIDtupla=(sID,)
        cursor=mydb.cursor()
        cursor.execute("SELECT COUNT(*) FROM FILE WHERE ID_UTENTE=%s",sIDtupla)
        filenum=cursor.fetchall()
        filenum=str(filenum[0][0]).ljust(3)

        cursor=mydb.cursor()
        cursor.execute("DELETE FROM FILE WHERE ID_UTENTE=%s",sIDtupla)
        mydb.commit()

        cursor=mydb.cursor()
        cursor.execute("DELETE FROM UTENTE WHERE SID=%s",sIDtupla)
        mydb.commit()
    except BaseException as error:
        print("ERRORE NEL LOGOUT"+error.msg)

    response="ALGO"+filenum
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
            # e del numero di file con stesso MD5 presenti
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
                        response=acceptLogout(packet)
                        print(f"La risposta al client è {response}")
                        dataSender(response)