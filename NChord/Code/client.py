import socket
import sys
import json


#Create a socket
soc = socket.socket()

try:

    soc.connect((sys.argv[1], int(sys.argv[2])))
    str = 'Hello there!'
    soc.send(str.encode())

    serverMessage = soc.recv(1024)

    msg = json.loads(serverMessage.decode())['data']

    print("Server Message: "+ msg[0])

    soc.close()

except Exception as e:
    print("Exception occured")