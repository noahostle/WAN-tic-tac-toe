import socket
import threading
import os

ip='127.0.0.1'
port=4444

max_connections = 2
clients=[]
players={}

lock=threading.Lock()


targetip='127.0.0.1'
targetport=8888

def upload_host():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as host:
		host.connect((targetip, targetport))

		host.send(b'Host')
		print(host.recv(1024).decode().strip())
		while True:
			dec = input(">>   ")
			host.send(dec.encode())
			if dec=="stop":
				sys.quit()


def handle_cli(cli):
	if len(clients) != 2:
		cli.sendall(b'Waiting for another player...\n\n')
	while len(clients) != 2:
		imstillwaiting=True

	cli.sendall(b'\nWelcome to tic tac toe!\n')
	cli.sendall(b'\nWhat is your name? >>   ')
	name = cli.recv(1024).decode().strip()

	with lock:
		players[name] = 'X' if len(players) == 0 else 'O'
		players[cli] = name


	cli.sendall(f'\n{"-"*os.get_terminal_size().columns}\n'.encode())
	cli.sendall(b'\nYou may have to wait for the other player to enter their name.\n\n')
	cli.sendall(b'Make a move by typing "row column" without quotes, eg. "1 2" for top middle\n')
	cli.sendall(f'\n{"-"*os.get_terminal_size().columns}\n'.encode())
	cli.sendall(f'\nYour symbol is {players[name]}\n\n'.encode())

def listen():
	with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as svr:
		svr.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		svr.bind((ip, port))
		svr.listen(max_connections)
		print('Server started, waiting for clients...')
		while len(players)!=4:
			if len(clients)!=2:
				cli, cliaddr = svr.accept()
				print(f'{cliaddr} connected\n')

				with lock:
					clients.append(cli)
				threading.Thread(target=handle_cli, args=(cli,)).start()
		return [cli, clients]

def validate(alpha, board):
	try:
		alpha[0] = int(alpha[0])
		alpha[2] = int(alpha[2])
	except:
		return False
	if len(alpha) != 3 or int(alpha[0])>3 or int(alpha[0])<1 or int(alpha[2])>3 or int(alpha[2])<1 or board[int(alpha[0])-1][int(alpha[2])-1] != '-':
		return False
	else:
		return True

def check_win(board):

	for symbol in ["X","O"]:
		for row in range(0,3):
			rowwin=True
			columnwin = True
			for column in range(0,3):
				if board[row][column] != symbol:
					rowwin = False
				if board[column][row] != symbol:
					columnwin = False

			if rowwin or columnwin:
				return 1

		mirror=[[board[0][2], 0, 0],
				[0, board[1][1], 0],
				[0, 0, board[2][0]]]
		diaboards = [board,mirror]
		for x in diaboards:
			diawin=True
			for d in range(0,3):
				if x[d][d] != symbol:
					diawin = False
			if diawin:
				return 1

	empty=False
	for x in range(0,3):
		for y in range(0,3):
			 if board[x][y] == "-":
			 	empty=True
			 	break
	if empty==False:
		return 2

	return 0



def start_game(cli,clients):
	go=0
	won=False
	board = [['-', '-', '-'], ['-', '-', '-'], ['-', '-', '-']]


	clients[0].send(f'Players: {list(players)[0]+", "+list(players)[2]}\n\n'.encode())
	clients[1].send(f'Players: {list(players)[0]+", "+list(players)[2]}\n\n'.encode())
	for l in board:
		clients[0].send((str(l)+"\n").encode())
		clients[1].send((str(l)+"\n").encode())



	while won==0:

		if go == 0:
			x=0
			y=1
		else:
			y=0
			x=1
		clients[x].send(b"\nIt's your go, enter move >>   ")
		clients[y].send(f"\nIt's {(players)[clients[x]]}'s go now".encode())
		turn = clients[x].recv(1024).decode().strip()
		alpha=list(turn)

		while not validate(alpha, board):
			clients[x].send(b"It's your go, enter move >>   ")
			turn = clients[x].recv(1024).decode().strip()
			alpha=list(turn)

		clients[0].send("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n".encode())
		clients[1].send("\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n\n".encode())
		
		board[int(alpha[0])-1][int(alpha[2])-1]=players[list(players)[x*2]]
		for l in board:
			clients[y].send((str(l)+"\n").encode())
			clients[x].send((str(l)+"\n").encode())

		go=y
		won = check_win(board)
	if won==1:
		clients[y].send((f"ERMMM... {list(players)[x*2]} JUST WON"+"\n").encode())
		clients[x].send(("ERMMM... YOU JUST WON"+"\n").encode())
		print(f'{list(players)[x]} just won.')
	elif won==2:
		clients[y].send((f"Stalemate."+"\n").encode())
		clients[x].send(("Stalemate.").encode())
		print(f'Stalemate.')
	else:
		print("WTF")

threading.Thread(target=upload_host, args=()).start()
args=listen()
start_game(args[0],args[1])
