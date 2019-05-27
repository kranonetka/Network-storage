import socket


def readexactly(connection: socket.socket, bytes_count: int):
	b = bytearray()
	while len(b) < bytes_count:
		part = connection.recv(bytes_count - len(b))
		if not part:
			raise IOError("Connection closed")
		b += part
	return bytes(b)


def read_message(connection: socket.socket):
	b = bytearray()
	while True:
		part_len = int.from_bytes(readexactly(connection, 2), "big")
		if part_len == 0:
			break
		b += readexactly(connection, part_len)
	return bytes(b)


def send_message(connection: socket.socket, msg: bytes):
	for chunk in (msg[i:i+65535] for i in range(0, len(msg), 65535)):
		connection.send(len(chunk).to_bytes(length=2, byteorder="big"))
		connection.send(chunk)
	connection.send(b"\x00\x00")


def main():
	ipaddr = input("ip: ")
	sock = socket.socket()
	sock.connect((ipaddr, 9090))
	while True:
		data_to_send = input(">>> ")
		for word in data_to_send.split():
			send_message(sock, word.encode())
		try:
			reply = read_message(sock)
		except IOError:
			exit(0)
		if data_to_send.split()[0] == "getfile":
			with open("reply", "wb+") as file:
				file.write(reply)
			print("Server reply writed into reply file")
		else:
			print("<<< " + reply.decode())


if __name__ == "__main__":
	main()
