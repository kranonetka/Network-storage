import socket

if __name__ == "__main__":
	sock = socket.socket()
	sock.connect(("localhost", 9090))
	while True:
		data_to_send = input(">>> ")
		sock.send(data_to_send.encode() + b"\x00")
		reply = b""
		for b in iter(lambda: sock.recv(1), b"\x00"):
			reply += b
		print("<<< " + reply.decode())