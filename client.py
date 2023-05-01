import socket
import threading

targetip="127.0.0.1"
targetport=8888


def recv():
	while True:
		print(server.recv(1024).decode())







with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as host:
		host.connect((targetip, targetport))

		host.send(b'Plyr')
		print(host.recv(1024).decode().strip())
		print(host.recv(1024).decode().strip())
		print(host.recv(1024).decode().strip())
		while True:
			prompt = input(" >>   ")
			host.send(prompt.encode())
			resp = host.recv(1024).decode().strip()

			resplit = resp.split(",")
			if len(resplit) ==2 and ":" not in resp:
				ip = resplit[0][2:-1]
				with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server:
					server.connect((ip, 4444))
					threading.Thread(target=recv).start()
					while True:
						server.send(input(" >>   ").encode())
			else:
				print(resp)

