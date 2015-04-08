import sys
import urllib2
import socket

BUFFER_SIZE = 4096

HOST = sys.argv[1]
PORT = int(sys.argv[2])

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect((HOST,PORT))

req = ("GET / HTTP/1.1\nHost: facebook.com\r\n\r\n")
print req
s.send(req)
response = s.recv(BUFFER_SIZE)
print response