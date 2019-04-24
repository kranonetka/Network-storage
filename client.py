import socket

def main():
	ipaddr = input("ip: ")
	sock = socket.socket()
	sock.connect((ipaddr, 9090))
	while True:
		data_to_send = input(">>> ")
		sock.send(data_to_send.encode() + b"\x00")
		reply = b""
		while True:
			reply += sock.recv(1)
			if not reply or reply[-1] == 0:
				break
		if not reply:
			print("Server closed connection")
			exit()
		reply = reply[:-1]
		print("<<< " + reply.decode())

if __name__ == "__main__":
	main()
