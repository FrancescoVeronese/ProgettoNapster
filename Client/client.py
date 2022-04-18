import socket
import hashlib
import os
import random

#INDICAZIONI GENERALI:
#NON usare cancelletti per riempire posti vuoti in stringhe, lasciare lo spazio vuoto (risolto)
#La parte di DOWNLOAD va sviluppata dopo il 14/04/2022, per il testing ora è lasciata a commento

#calcolo md5 metodo
def calcmd5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
    
def login(ip, porta):
    ipsend=ip.ljust(15)
    porta=str(porta)
    portsend=porta.ljust(5) #porta da cui il client si metterà in ascolto per ricevere richieste download
    #stringa di risposta
    response="LOGI"+ipsend+portsend
    return response
    
def aggiungi(sessionID):
    nameFile = input("Scrivere nome file")
    while(len(nameFile)>100):#accettare solo nomi di file minori di 100 caratteri(byte)
        nameFile = input("Scrivere nome file")
    md5 = calcmd5(nameFile)
    nameFile_send=nameFile.ljust(100)
    response="ADDF"+str(sessionID)+str(md5)+str(nameFile_send)
    return response
def delete(sessionID):
    nameFile = input("Scrivere nome file")
    md5 = calcmd5(nameFile)
    namefile=namefile.ljust(100)
    response="DELF"+str(sessionID)+str(md5)
    return response

def find(sessionID):
    string = input("Scrivere stringa di ricerca")
    string=string.ljust(20)
    response="FIND"+str(sessionID)+str(string)
    return response
    
def logout(sessionID):
    response="LOGO"+str(sessionID)
    return response
'''
def cliedownload(sessionID):
    response="RETR"+str(sessionID)
    return response
'''
'''
def servdownload(sessionID):
    response="RREG"+str(sessionID)
    return response
'''
""" 
def download(serverhost, serverport, filecode):  # funzione per scaricare un file da un altro peer
        s2 = socket.socket(socket.AF_INET,socket.SOCK_STREAM) # connessione al peer
        s2.connect((serverhost,serverport))
        print("Client connesso e pronto per scaricare file")
        response = cliedownload(filecode) # messaggio al peer contenente l'md5 del file
        s2.send(response.encode())
        path = os.getcwd() # cartella in cui installare il file (cartella corrente)
        data = s2.recv(1024) # grandezza del file da ricevere
        totalRecv = 0
        name = input("Inserisci nome da dare al file")
        f = open(path + '/' + name, 'wb')
        f.write(data)
        filesize = data
        message = s2.recv(1024).decode
        if(message == "ARET"): # controllo sul primo messaggio e inizio scaricamento
            while totalRecv < filesize: # confronto quanti dati scaricati con la grandezza del file da scaricare
                data = s2.recv(1024)
                totalRecv += 1024
                f.write(data)
            print("File is downloaded Successfully")
            s2.close()
"""
ip = ""
remoteip="25.13.127.60"
porta = 80
directory = os.getcwd()
sessionID = ""
t = 1
s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect((remoteip,porta))
s1 = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s1.bind((ip, porta))
listenport=random.randint(50000,60000)


response=login(remoteip, listenport)
s.send(response.encode())
logaccept = s.recv(1024).decode()
print(f"Ricevuto {logaccept}")
sessionID=logaccept[4:20]
print(f"Il sessionID assegnato è {sessionID}")

s1.listen(10)
pid = os.fork()
while True:
    if pid > 0:
        scelta = input("Scelta azione:\n 1 per Aggiungere un file\n 2 per Rimuovere un file\n 3 per Ricercare un file\n 4 per Scaricare un file\n 5 per fare Logout")
        if(scelta==1):
                response = aggiungi(sessionID)
                s.send(response.encode())
                risultato=s.recv(1024).decode()

        else:  
            if(scelta==2):
                response = delete(sessionID)
                s.send(response.encode())
                
            else:
                if(scelta==3):
                    response = find(sessionID)
                    s.send(response.encode())
                else:
                    if(scelta==4):
                        '''
                        port = input("Inserisci porta del peer")
                        host = input("Inserisci indirizzo del peer")
                        filename = input("Inserisci nome file")
                        filecode = calcmd5(filename)
                        download(host, port, filecode)
                        response = servdownload(sessionID)
                        s.send(response.encode()) # informo il server dello scaricamento
                        '''
                    else:
                        if(scelta==5):
                            response = logout(sessionID)
                            s.send(response.encode())
                            s.close()
    else:
        conn, address = s.accept() # connessione con peer richiedente
        
        try:
            filename = conn.recv(1024).decode()
            if os.path.exists(directory + '/' + filename):
                filesize = os.path.getsize(directory + '/' + filename)
                if filesize > 0:
                    conn.send(str(filesize))
                    with open(directory + '/' + filename, 'rb') as f:
                        message = "ARET"
                        conn.send(message.encode())
                        bytes = f.read(1024)
                        conn.send(bytes)
                        while bytes != "":
                            bytes = f.read(1024)
                            conn.send(bytes)
                else:
                    conn.send("File vuoto")
            else:
                conn.send("Percorso non trovato")
        except:
            conn.close()
            
