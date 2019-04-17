import socket
from multiprocessing import Process, Manager


#set <key> : <val>
#get <key>
#del <key>


def main(storage, connection):
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
		elif cmd.startswith("get "):
			pass
		elif cmd.startswith("del "):
			pass
		else:
			pass #unrecognized command


if __name__ == "__main__":
	storage = Manager().dict()

	sock = socket.socket()
	sock.bind(("", 9090))
	sock.listen(5)
	while True:
		conn, addr = sock.accept()
		print("New connection from {}".format(addr))
		proc = Process(target=main, args=(storage, conn))
		proc.daemon = True
		proc.start()
