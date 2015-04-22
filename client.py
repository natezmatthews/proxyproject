import sys
import urllib2
import socket

BUFFER_SIZE = 4096

HOST = sys.argv[1]
PORT = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))

req = ("GET / HTTP/1.1\nHost: lucyq.github.io\r\n\r\n")
print req
s.send(req)
while 1:
	response = s.recv(BUFFER_SIZE)
	if len(response) > 0:
		print response