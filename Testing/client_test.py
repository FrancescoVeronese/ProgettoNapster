#AREA DI TESTING PER LE SINGOLE FUNZIONALITA---client
import socket
import hashlib
response=""
'''
def login(ip, porta):
    #stringa di risposta
    response="LOGI"+str(ip)+str(porta)
    return response
'''
#calcolo md5 metodo
def calcmd5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


def aggiungi(sessionID):
    nameFile = input("Scrivere nome file")
    while(len(nameFile)>100): #accettare solo nomi di file minori di 100 caratteri(byte)
        nameFile = input("Scrivere nome file")
    md5 = calcmd5(nameFile)
    num=100  #la stringa del nome da inviare è 100 byte
    chars=len(nameFile) #i caratteri della stringa filename presa in input sono:
    blanks=num-chars #i caratteri da lasciare vuoti sono:
    #si crea la stringa vuota da namefile+ posti blanks
    nameFile_send=nameFile + ''*blanks
    print(nameFile_send) #per testing
    response="ADDF"+str(sessionID)+str(md5)+str(nameFile_send)
    return response

aggiungi("SONOUNSESSIONID")
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("",50000))
s.send(response.encode())

response=s.recv(1024).decode()
print(response)
