import socket
import time
import sys
import select

NUM_CLIENTS = 1
BUFFER_SIZE = 4096

class Server:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((host, port))
        self.server.listen(NUM_CLIENTS)

    def readFromClient(self):
        cli_sockfd, cli_addr = self.server.accept()
        self.data = cli_sockfd.recv(BUFFER_SIZE)
        return self.data

class Client:
    def __init__(self, host, port):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, port))
        except Exception, e:
            print e

    def communicate(self, data):
        self.client.send(data)
        resp = ''
        while 1:
            read = self.client.recv(BUFFER_SIZE)
            if len(read) == 0:
                break
            resp += read
        print findLinks(resp)

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
        client.communicate(req)

    except KeyboardInterrupt:
        print "Ctrl C - Stopping server"
        sys.exit(1)