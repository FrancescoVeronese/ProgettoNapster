import threading
from pathlib import Path
from os.path import exists
import os,random
import signal
import socket, sys
import uuid

import hashlib



def conn_close(signal,frame):
    logout(sessionID)


def thisHost(localip):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ip=localip
    s.close()
    return str(ip)
def adjustLength(stringa, dim):
    tmp=""
    for n in range(0,dim-len(stringa)):
        tmp+="0"
        tmp+=stringa
    return tmp

def MD5generator(filename):
    hash_md5 = hashlib.md5()
    with open(filename, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest().upper()

def localServer(localport,fileNameList,fileMD5List):
    locserver=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    locserver.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    locserver.bind(("",int(localport)))
    locserver.listen(10)
    while True:
        peer,addr= locserver.accept()
        pid=os.fork()
        if(pid==0):
            request=peer.recv(1024).decode()
            verb=request[0:4]
            if(verb=="RETR"):
                MD5=request[4:36]
                for file in fileMD5List:
                    if(MD5==file):
                        print("Il file è stato trovato\n")
                        fileSend(peer,file,fileNameList) #invio file nella socket con peer del file con MD5 corrispondente
                    else:
                        print("File non esistente\n")
                        response="ARET000000"
                        peer.send(str(response).encode())

            peer.close()
            exit()
def fileSend(socket,file,fileNameList):
    #10 Byte, 4 ARET, 6 numero chunk
    pkt="ARET"
    filename=""
    #trovare indice del MD5 (stesso indice del corrispettivo nome file in filenamelist)
    for x in range (0,len(fileMD5List)):
        if(file==fileMD5List[x]):
            filename=fileNameList[x]

    fd = os.open(filename, os.O_RDONLY)
    fileDirectory=os.getcwd()
    size=fileDirectory.getsize(filename) #grandezza file
    lastchunk=size%4096
    numchunk=size//4096  
    if(lastchunk!=0):numchunk+=1
    pkt+=adjustLength(str(numchunk),6)
    socket.send(pkt.encode()) #invia al peer numero di chunk
    pkt=""  #singolo chunk
    for n in range(0,numchunk): #i chunk da mandare sono n
        pkt+="04096"  #invia la grandezza del chunk
        pkt+=os.read(fd,4096) #invia le informazioni del chunk stesso
        socket.send(pkt)
        pkt=""
    if(lastchunk!=0): #l'ultimo chunk con grandezza minore a 4096 viene mandato alla fine
        pkt+=adjustLength(str(lastchunk),5)
        pkt+=os.read(fd,4096)
        socket.send(pkt)
    os.close(fd)

def login(localport,localip): #finito
    localport=str(localport)#porta da cui il client si metterà in ascolto per ricevere richieste download
    _localip=thisHost(localip)
    #stringa di risposta
    response="LOGI"+localip.ljust(15)+localport.ljust(5)
    print(localip)
    print(localport)
    servcon=dataSender(remoteip,80,response) #invio stringa login
    packet=servcon.recv(1024).decode()
    servcon.close()
    return packet
        
def logout(sessionID):
    logoutstring=""
    response="LOGO"+sessionID
    servcon=dataSender(remoteip,80,response)
    logoutstring=servcon.recv(1024).decode()
    servcon.close()
    verb=logoutstring[0:4]
    filenum=logoutstring[4:7] #numero di file rimossi
    print("\n"+verb+" I file rimossi dal DB del server sono"+filenum)
    print("LOGOUT EFFETTUATO")
    os.abort() #chiusura processo

def dataSender(serverip,serverport,data): #finito
    try:
        servcon = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
        servcon.connect((serverip,serverport))
    except BaseException as err:
        print(err)
        exit()
        
    servcon.send(str(data).encode())
    return servcon

def addFile(sessionID):
    nameFile = input("Scrivere nome file ")
    while(len(nameFile)>100):#accettare solo nomi di file minori di 100 caratteri(byte)
        nameFile = input("Scrivere nome file ")
    md5 = MD5generator(nameFile)
    nameFile_send=nameFile.ljust(100)
    addstring="ADDF"+str(sessionID)+str(md5)+str(nameFile_send)
    servcon=dataSender(remoteip,80,addstring) #aggiunta al server
    servstring=servcon.recv(1024).decode()
    servcon.close()
    verb=servstring[0:4]
    filenum=servstring[4:7] #versioni del file presenti nel DB con stesso MD5
    print(verb, "Il numero di file inseriti con stesso MD5 è ",filenum)
    return addstring

def delFile(sessionID):
    nameFile = input("Scrivere nome file ")
    while(len(nameFile)>100):#accettare solo nomi di file minori di 100 caratteri(byte)
        nameFile = input("Scrivere nome file ")
    md5 = MD5generator(nameFile)
    delstring="DELF"+str(sessionID)+str(md5)
    servcon=dataSender(remoteip,80,delstring) #aggiunta al server
    servstring=servcon.recv(1024).decode()
    servcon.close()
    verb=servstring[0:4]
    filenum=servstring[4:7] #quante versioni del file erano presenti nel DB
    print(verb,"Il numero di file eliminati con stesso MD5 è",filenum)
    return delstring

def searchFile(sessionID):
    searchString=str(input("Inserire stringa di ricerca:\n "))
    while(len(searchString)>20): #meno di 20 byte
        searchString=str(input("Inserire stringa di ricerca maggiore di 20 caratteri:\n "))
    #verbo find 0-4, session id 4-20 e stringa ricerca 20-40
    searchpkt="FIND"+sessionID+searchString
    servcon=dataSender(remoteip,80,searchpkt) #invio ricerca file
    servstring=servcon.recv(7).decode() #il verbo e il numero di file con searchstring
    numfile=int(servstring[4:7])

    for n in range(0,numfile): #ogni singolo file
        fileInfo=servcon.recv(152).decode() #32 md5,100 filename, 15 ip, 5 porta
        md5=fileInfo[0:32]
        filename=fileInfo[32:132]
        ipAddress=fileInfo[132:147]
        port=fileInfo[147:152]
        peer=(ipAddress,port,filename,md5)
        print("L'utente %s:%s,\n ha il file con nome:%s e MD5 %s",peer)
    servcon.close()
    return 0
def downloadFile(sessionID,md5,peerIP,peerPORT,localdir):
    print("Inserisci il nome del file da salvare ")
    fileName=str(input())
    pkt="RETR"+md5
    peer = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    try:
        peer.connect((peerIP,int(peerPORT)))
    except BaseException as err:
        print("il server non è raggiungibile, riprova più tardi\n %s",err.msg)
    peer.send(pkt.encode())
    chunknumpacket=peer.recv(10)
    command=chunknumpacket[0:4]
    print("%s\n",command)
    if(command=='ARET'):
        pid=os.fork()
        if(pid==0):
            chunk=int(chunknumpacket[4:10])
            if(chunk==0):
                print("il file è vuoto oppure non è più in condivisione\n")
                exit()
            if(exists(localdir+"/"+fileName)): os.remove(localdir+"/"+fileName)
            fd = os.open(localdir+"/"+fileName, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o777)
            for ck in range(0,chunk):
                stream=peer.recv(peer.recv(5))
                os.write(fd,stream)
            os.close(fd)
            peer2=dataSender(remoteip,80,"RREG"+sessionID.ljust(16)+md5.ljust(32)+peerIP.ljust(15)+peerPORT.ljust(5))
            downloaded=peer2.recv(9).decode()
            num=downloaded[4:9]
            print(f"il file è stato scaricato{int(num)} volte")
            peer2.close() #chiusura seconda socket legata al server
            peer.close() #chiusura socket legata al client inviante il file
    else:
        print("ERRORE\n")
        peer.close()
        exit()

localdir=os.getcwd()
sessionID=""
recvpacket=""
remoteip=str(sys.argv[1])
localip=str(sys.argv[2])
listenport=random.randint(50000,60000) #porta d acui il client ascolta per eventuali richieste di file dai peer
recvpacket=login(listenport,localip)
sessionID=recvpacket[4:20]
if(sessionID=="0000000000000000"):
    print("ERRORE LOGIN")
    exit()

signal.signal(signal.SIGINT, conn_close) #nel caso di pressione ctrl+c si chiude la connessione al server e il record viene eliminato dal DB

directory = os.listdir('.') #file nella directory locale del programma client
print(directory)
 
fileNameList=[]
fileMD5List=[]
for filename in directory:
    
    fileNameList.append(filename)
    fileMD5List.append(MD5generator(filename))

#creazione thread che controlla la parte server del client

server_client=threading.Thread(target=localServer,args=(listenport,fileNameList,fileMD5List)) 
server_client.start()


while True:
    scelta=int(input("Inserire:\n 0 per LOGOUT\n 1 per Aggiunta file\n 2 per Rimozione file\n 3 per Ricerca\n 4 per Download\n"))
    if(scelta==0):
        logout(sessionID)
    else:
        if(scelta==1):
            addFile(sessionID)      
        else:
            if(scelta==2):
                delFile(sessionID)
            else:
                if(scelta==3):
                    searchFile(sessionID)
                else:
                    if(scelta==4):
                        peerIP=input("Inserire IP peer da cui scaricare il file\n")
                        peerPORT=input("Inserire la porta del peer\n")
                        fileMD5=input("Inserire MD5 del file da scaricare\n")
                        downloadFile(sessionID,fileMD5,peerIP,peerPORT,localdir)
                    else:
                        print("PERMESSO NEGATO\n")