import socket
from multiprocessing import Process, Manager


data = Manager.dict()


#set <key> : <val>
#get <key>
#del <key>


def main(connection):
	while True:
		cmd = b""
		while True:
			data = connection.recv(1024)
			if not data:
				break
			cmd += data
		cmd = cmd.decode()
		if cmd.startswith("set "):
			pass
		if cmd.startswith("get "):
			pass
		if cmd.startswith("del "):
			pass


if __name__ == "__main__":
	sock = socket.socket()
	sock.bind(("", 9090))
	sock.listen(5)
	while True:
		conn, addr = sock.accept()
		print("New connection from {}".format(addr))
		proc = Process(target=main, args=(conn,))
		proc.daemon = True
		proc.start()
