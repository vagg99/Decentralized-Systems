import socket
import sys
import threading
import json

jobs=[]

address = sys.argv[1]
port = int(sys.argv[2])

soc=socket.socket()
soc.bind((address,port))
soc.listen()

def listener():

    while True:
        (clientConnection, clientAddress) = soc.accept()
        clientMessage = clientConnection.recv(1024)
        if clientMessage:
            jobs.append((clientConnection,clientMessage))

def worker():
    while True:
        if jobs:
            msg = jobs.pop(0)

            data = {'data' :["dataaaaa"]}
            data =json.dumps(data)
            
            msg[0].send(bytes(data, encoding='utf-8'))

listener_thread = threading.Thread(target=listener)
worker_thread = threading.Thread(target=worker)


listener_thread.start()
worker_thread.start()

