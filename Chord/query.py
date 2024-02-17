import socket
import os
import sys

def main():
	#port = input("Give the port of a network node: ")
	ip = "127.0.0.1"
	port = 80
    
	port = int(input("Give the port of a network node: "))
	while(True):
		
		try:
			sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
			sock.connect((ip,port))
		
			print("\n")
			print("************************MENU*************************")
			print("PRESS ***********************************************")
			print("1. TO SEARCH *****************************************")
			print("CTRL+C. TO EXIT ******************************************")
			print("*****************************************************")
			choice = input()

			if(choice == '1'):
				key = input("Enter the key to search for: ")
				message = "search|" + str(key)
				sock.send(message.encode('utf-8'))
				data = sock.recv(1024)
				data = str(data.decode('utf-8'))
				print("The value corresponding to the key is : ",data)

	
			else:
				print("Invalid choice!")
				
		except KeyboardInterrupt:
			print('Exiting..')
			try:
				sys.exit(0)
			except SystemExit:
				os._exit(0)
		except:
			print("Error concerning the connection, try a different port..")
			port = int(input("Give the port of a network node: "))
		
if __name__ == '__main__':
	try:
		main()
	except KeyboardInterrupt:
		print('Exiting..')
		try:
			sys.exit(0)
		except SystemExit:
			os._exit(0)