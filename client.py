import socket
import random
import sys
import time

alph = bytes((c for c in range(ord("a"), ord("z")+1)))

if __name__ == "__main__":
	sock = socket.socket()
	sock.connect(("localhost", 9090))
	while True:
		msg = "Hello from {}".format(sys.argv[1])
		sock.send(msg.encode())
		time.sleep(1)
