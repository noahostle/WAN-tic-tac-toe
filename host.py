ip='127.0.0.1'
port=8888
import socket
import threading
import select


lock=threading.Lock()
hosts={}


def listen():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as svr:
		svr.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		svr.bind((ip, port))
		svr.listen(99)
		print('Server started, waiting for hosts...')
		while True:
			host, hostaddr = svr.accept()
			typehelper = host.recv(1024).decode().strip()
			if typehelper=="Host":
				threading.Thread(target=hold_host, args=(host,hostaddr)).start()
			else:
				threading.Thread(target=hold_player, args=(host,hostaddr)).start()
			print(f'{hostaddr} connected as {typehelper}\n')
			

def hold_host(host,hostaddr):
	print(f"Asking server name for {hostaddr}")
	host.send(b'Enter your server name >>   ')
	name = host.recv(1024).decode().strip()

	with lock:
		hosts[name]=hostaddr
	print(hosts)

	host.send(b'Type "stop" at any time to stop your server')
	stopcommand="hi"

	while stopcommand != "stop":
		ready = select.select([host], [], [], 2)
		if ready[0]:
			try:
				stopcommand = host.recv(1024).decode().strip()
			except:
				break

	print(f"[{name}] disconnected")
	with lock:
		hosts.pop(name)
	print(hosts)
	host.close()

def hold_player(plyr, plyraddr):
	plyr.send(b'hosts:\n\n')
	plyr.send(str(hosts).encode())
	plyr.send(b'\n\nEnter "refresh" to refresh server list, or a server name to connect\n')
	while True:
		refresh = plyr.recv(1024).decode().strip()
		if refresh=="refresh":
			plyr.send((".\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n"+str(hosts)).encode())
		elif refresh in hosts:
			plyr.send(str(hosts[refresh]).encode())
		else:
			plyr.send(b' >>   ')



listen()