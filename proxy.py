# proxy.py
# COMP 112 Project 5
# Lucy Qin and Nate Matthews

import socket
import sys
import select

NUM_CLIENTS = 1
BUFFER_SIZE = 4096

# Server class handles communication with the client
class Server:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(NUM_CLIENTS)

    def readFromClient(self):
        self.cli_sockfd, cli_addr = self.server.accept()
        self.data = self.cli_sockfd.recv(BUFFER_SIZE)
        return self.data

    def sendToClient(self, data):
        self.cli_sockfd.send(data)

# Client class handles communication with the destination server
class Client:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, port))
        except Exception, e:
            print e

    def sendToServer(self, data):
        self.client.send(data)
    
    def readFromServer(self):
        resp = ''
        while 1:
            read = self.client.recv(BUFFER_SIZE)
            if len(read) == 0:
                break
            resp += read
        findLinks(resp)
        return resp

# findLinks function finds all HTML links in a document
def findLinks(document):
    linkstr = "<a href="
    searchfrom = 0
    while 1:
        try:
            startind = document.index(linkstr, searchfrom) + len(linkstr)
            if startind == -1:
                break
            endind = document.index(document[startind], startind + 1)
            if endind == -1:
                break
            print document[(startind + 1):endind]
            searchfrom = endind + 1
        except ValueError:
            break

if __name__ == '__main__':
    try:
        if len(sys.argv) != 3:
            print "Usage: " + sys.argv[0] + "[hostname] [port number]"
            sys.exit(1)
        hostname = sys.argv[1]
        portno = int(sys.argv[2])
        
        server = Server(hostname, portno)
        req = server.readFromClient()
        
        elems = req.split()
        client = Client(elems[4], 80)
        client.sendToServer(req)
        resp = readFromServer()
        server.sendToClient(resp)

    except KeyboardInterrupt:
        print "Ctrl C - Stopping server"
        sys.exit(1)