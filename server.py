import socket
import re
from multiprocessing import Process, Manager


def main(connection, storage):
	while True:
		cmd = b""
		while True:
			cmd += connection.recv(1)
			if not cmd or cmd[-1] == 0:
				break
		if not cmd:
			exit(0)
		cmd = cmd[:-1]
		match = re.fullmatch(b"set (\w+) = (\w+)", cmd)
		if match:
			storage[match.group(1)] = match.group(2)
			connection.send(b"ok\x00")
			continue
		match = re.fullmatch(b"del (\w+)", cmd)
		if match:
			connection.send(b"ok\x00" if storage.pop(match.group(1), None) else b"key doesn't exists\x00")
			continue
		match = re.fullmatch(b"get (\w+)", cmd)
		if match:
			connection.send(storage[match.group(1)] + b"\x00" if match.group(1) in storage else b"key doesn't exists\x00")
			continue
		if cmd == b"exit":
			connection.shutdown(socket.SHUT_RDWR)
			connection.close()
			exit(0)
		connection.send(b"unrecognized command\x00")


if __name__ == "__main__":
	storage = Manager().dict()

	sock = socket.socket()
	sock.bind(("", 9090))
	sock.listen(5)
	while True:
		conn, addr = sock.accept()
		print("New connection from {}".format(addr))
		proc = Process(target=main, args=(conn, storage))
		proc.daemon = True
		proc.start()
