from _thread import *
import socket
import sys 
import os 
import time
import sched
from threading import Timer, Thread
import selectors
import constants

DATA = {}

SERVER_INDEX = 0
IP, STORE_PORT = constants.ORIGIN_SERVERS_STORE_CREDENTIALS[SERVER_INDEX]
IP, REQUEST_PORT = constants.ORIGIN_SERVERS_REQUEST_CREDENTIALS[SERVER_INDEX]
#SYNC_PORT = 
store_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
store_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
store_s.bind(('', STORE_PORT)) 
store_s.listen(0)

request_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
request_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
request_s.bind(('', REQUEST_PORT)) 
request_s.listen(0)

sync_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sync_s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		

def synchronise():
	while(True):
		IP, PORT = "localhost", constants.SYNC_PORT_2
		try:
			sync_s.connect((IP, PORT))
			print(f"Syncing with {IP} AT {PORT}")
			break
		except:
			print(f"COULD NOT SYNC WITH {IP} AT {PORT}")
			print("Retrying.. ")
			time.sleep(1)

	while(True):
		try:
			n_1 = len(DATA.keys())
			sync_s.send(n_1)
			sync_s.close()
			break
		except:
			print("Could not sync! Retrying..")
	
def store_content():
	while(True):
		store_c, store_addr = store_s.accept()
		print("Accepted store connection from ", store_addr)
		name, content = store_c.recv(1024).decode("utf-8").split("/")
		DATA[name] = content
		store_c.close()
		print("Data Stored!")

def content_requests_handler():
	while(True):
		request_c, request_addr = request_s.accept()
		print("Accepted request from", request_addr)
		name = request_c.recv(1024).decode("utf-8").strip()
		print(name)
		if(name in DATA.keys()):
			request_c.send(DATA[name].encode())
		else:
			request_c.send("Data not found".encode())
		request_c.close()


if __name__ == '__main__':

	threads = []
	
	t1 = Thread(target = store_content)
	threads.append(t1)
	t1.start()
	
	t2 = Thread(target = content_requests_handler)
	threads.append(t2)
	t2.start()

	t3 = Thread(target = synchronise)
	threads.append(t3)
	t3.start()

	for t in threads:
		t.join()
