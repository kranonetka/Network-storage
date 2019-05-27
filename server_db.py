import socket
import re
import multiprocessing
from multiprocessing import synchronize
import sqlite3


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
	for part_len in iter(lambda: int.from_bytes(readexactly(connection, 2), "big"), 0):
		b += readexactly(connection, part_len)
	return bytes(b)


def send_message(connection: socket.socket, msg: bytes):
	for chunk in (msg[i:i+65535] for i in range(0, len(msg), 65535)):
		connection.send(len(chunk).to_bytes(length=2, byteorder="big"))
		connection.send(chunk)
	connection.send(b"\x00\x00")


def key_exists(db: sqlite3.Connection, lock: multiprocessing.synchronize.Lock, key: str) -> tuple:
	cursor = db.cursor()
	lock.acquire()
	exists = cursor.execute("""
		SELECT key, value
		FROM storage
		WHERE key=?;
		""", 
		(key,)
	).fetchone()
	lock.release()
	cursor.close()
	return exists


def set_val(db: sqlite3.Connection, lock: multiprocessing.synchronize.Lock, key: str, val: str) -> bytes:
	exists = key_exists(db, lock, key)
	cursor = db.cursor()
	if exists:
		lock.acquire()
		cursor.execute("""
			UPDATE storage
			SET value = ?
			WHERE key = ?;
			""",
			(val, key)
		)
		db.commit()
		lock.release()
		msg = exists[0].encode()+b":"+exists[1].encode()+b" -> "+key.encode()+b":"+val.encode()
	else:
		lock.acquire()
		cursor.execute("""
			INSERT INTO storage
			VALUES (?, ?);
			""",
			(key, val)
		)
		db.commit()
		lock.release()
		msg = b"new"
	cursor.close()
	return msg


def del_by_key(db: sqlite3.Connection, lock: multiprocessing.synchronize.Lock, key: str) -> bytes:
	exists = key_exists(db, lock, key)
	if exists:
		cursor = db.cursor()
		lock.acquire()
		cursor.execute("""
			DELETE FROM storage
			WHERE key=?;
			""",
			(exists[0],)
		)
		db.commit()
		lock.release()
		cursor.close()
		msg = b"ok"
	else:
		msg = b"key doesn't exists"
	return msg


def get_by_key(db: sqlite3.Connection, lock: multiprocessing.synchronize.Lock, key: str) -> bytes:
	exists = key_exists(db, lock, key)
	cursor = db.cursor()
	if exists:
		lock.acquire()
		value = cursor.execute("""
			SELECT value FROM storage WHERE key=?;
			""",
			(exists[0],)
		).fetchone()
		lock.release()
		msg = value[0].encode()
	else:
		msg = b"key doesn't exists"
	cursor.close()
	return msg


def save_file(lock: multiprocessing.synchronize.Lock, filename: str, content: bytes) -> bytes:
	lock.acquire()
	try:
		with open(filename, "wb") as file:
			file.write(content)
		msg = b"ok"
	except FileNotFoundError:
		with open(filename, "wb+") as file:
			file.write(content)
		msg = b"new"
	lock.release()
	return msg

def get_file(lock: multiprocessing.synchronize.Lock, filename: str) -> bytes:
	lock.acquire()
	try:
		with open(filename, "rb") as file:
			content = file.read()
	except FileNotFoundError:
		content = b""
	lock.release()
	return content


def main(connection: socket.socket, lock: multiprocessing.synchronize.Lock):
	db = sqlite3.connect("storage.db")
	while True:
		cmd = read_message(connection)
		if cmd == b"set":
			key = read_message(connection).decode()
			value = read_message(connection).decode()
			msg = set_val(db, lock, key, value)
			send_message(connection, msg)
		elif cmd == b"del":
			key = read_message(connection).decode()
			msg = del_by_key(db, lock, key)
			send_message(connection, msg)
		elif cmd == b"get":
			key = read_message(connection).decode()
			msg = get_by_key(db, lock, key)
			send_message(connection, msg)
		elif cmd == b"exit":
			connection.shutdown(socket.SHUT_RDWR)
			connection.close()
			db.close()
			exit()
		elif cmd == b"setfile":
			filename = read_message(connection).decode()
			content = read_message(connection)
			msg = save_file(lock, filename, content)
			send_message(connection, msg)
		elif cmd == b"getfile":
			filename = read_message(connection).decode()
			content = get_file(lock, filename)
			send_message(connection, content)
		else:
			send_message(connection, b"unrecognized command")


if __name__ == "__main__":
	lock = multiprocessing.Lock()
	db = sqlite3.connect("storage.db")
	cursor = db.cursor()
	cursor.execute("""
		CREATE TABLE IF NOT EXISTS storage
		(key TEXT PRIMARY KEY, value TEXT);
	""")
	db.commit()
	cursor.close()
	db.close()
	sock = socket.socket()
	sock.bind(("", 9090))
	sock.listen(5)
	while True:
		conn, addr = sock.accept()
		print("New connection from {}".format(addr))
		proc = multiprocessing.Process(target=main, args=(conn, lock))
		proc.daemon = True
		proc.start()
