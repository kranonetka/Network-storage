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
	filepath = input("path to file: ")
	sock = socket.socket()
	sock.connect((ipaddr, 9090))
	with open(filepath, "rb") as file:
		filename = file.name
		data_to_send = file.read()
	print(filename)
	send_message(sock, b"setfile")
	send_message(sock, filename.encode())
	send_message(sock, data_to_send)
	reply = read_message(sock)
	send_message(sock, b"exit")
	print(reply.decode())


if __name__ == "__main__":
	main()
