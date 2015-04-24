import sys

try: 
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse


import socket

BUFFER_SIZE = 4096

HOST = sys.argv[1]
DEST_HOST = sys.argv[2]
DEST_PATH = sys.argv[3]
PORT = int(sys.argv[4])


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))

req = ("GET " + DEST_PATH + " HTTP/1.1\nHost: " + DEST_HOST + "\r\n\r\n")
print (req)
s.send(req.encode('utf-8'))
f = open("output.html","w")
while 1:
	response = (s.recv(BUFFER_SIZE)).decode('utf-8')
	print("Receivd response, writing to file")
	if len(response) > 0:
		f.write(response)
f.close()
sys.exit("Done!")


