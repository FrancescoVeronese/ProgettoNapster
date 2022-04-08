#AREA DI TESTING PER LE SINGOLE FUNZIONALITA---client
import socket

message="LOGI"
response=""
s=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.connect(("",80))
s.send(message.encode())

response=s.recv(1024).decode()
print(response)
