import socket 
from time import sleep

ip = "127.0.0.1"
port = 3001

# remove all blank/new lines from file
with open('scientist_info.txt') as reader, open('scientist_info.txt', 'r+') as writer:
  for line in reader:
    if line.strip():
      writer.write(line)
  writer.truncate()

# initialize the connection

# save each entry with 'Education' as the key
cnt = 0
with open('scientist_info.txt') as f:

    temp = ['null','null']
    while True:
        
        
        line = f.readline()
        if not line:
            break
        
        if(cnt%3 == 0):
           temp[0] = line.strip()
           temp[0] = temp[0].replace("Surname:", "") 
           
        elif (cnt%3 == 1): 
            temp[1] = line.strip()
            temp[1] = temp[1].replace("Awards:", "") 

        elif (cnt%3 == 2): 
            sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sock.connect((ip,port))

            line = line.replace("Education:", "") 
            message = "insert|" + line.strip() + ":" + temp[0] +"," + temp[1]
            sock.send(message.encode('utf-8'))
            sock.close()

        cnt = cnt + 1    

