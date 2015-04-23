# proxy.py
# COMP 112 Project 5
# Lucy Qin and Nate Matthews

import socket
import sys
import json
import select
import httplib
import urlparse
import pexpect
from bs4 import BeautifulSoup

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
    def __init__(self, request, port):
        elems = request.split()
        if len(elems) == 0:
            sys.exit("Error: Request does not contain separatable words")
        elif elems[0] != "GET":
            sys.exit("Error: Proxy can only handle HTML GET requests")
        elif elems[3] == "Host:":
            host = elems[4]
            print "Client host: ", host
            self.fullpath = elems[4] + elems[1]
            print "Client fullpath: ", self.fullpath
        else:
            host = elems[1]
            print "Client host: ", host
            self.fullpath = elems[1]
            print "Client fullpath: ", self.fullpath

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, port))
        except Exception, e:
            raise e

    def sendToServer(self, data):
        self.client.send(data)
    
    def readFromServer(self):
        resp = ''
        while 1:
            read = self.client.recv(BUFFER_SIZE)
            if len(read) == 0:
                break
            resp += read
        return findLinks(resp, self.fullpath)

def pingResult(netloc):
    try:
        child = pexpect.spawn('ping -c 3 ' + netloc)
    except Exception, e:
        raise e
    while 1:
        cur = child.readline()
        if not cur: break
        prev = cur
    return prev

def geoIP(netloc):
    try:
        conn = httplib.HTTPConnection("freegeoip.net")
    except Exception, e:
        raise e
    conn.request("GET", "/csv/" + netloc)
    res = conn.getresponse()
    return res.read()

def getLinkInfo(uri, origuri):
    parsed = urlparse.urlparse(uri)
    netloc = parsed.netloc
    print "Netloc:",netloc
    if netloc == "":
        # CASE: Relative URI:
        parsed2 = urlparse.urlparse("http://" + origuri)
        netloc = parsed2.netloc
        print "Updated netloc:",netloc
        i = (origuri.index(netloc) + len(netloc))
        k = origuri.rindex("/")
        print "i, k:",i,k
        path = parsed.path
        if path and (path[0] != "/"):
            path = "/" + path
        forreq = origuri[i:k] + path
        print "Forreq:",forreq
    else:
        # CASE: Absolute URI:
        i = (uri.index(netloc) + len(netloc))
        print "i:",i
        forreq = uri[i:]
        print "Forreq:",forreq
    
    # print "parsed.path: ", parsed.path
    # path = parsed.path
    # if path:
    #     uri = "http://" + dapath
    #     if(path[0] != "/"):
    #         uri += "/"
    #     uri += path

    # print "HeadReq: ", uri

    conn = httplib.HTTPConnection(netloc)
    try:
        conn.request("HEAD", forreq)
        res = conn.getresponse()
    except Exception, e:
        return "Error: Not a valid link"
    if (res.status == 200) or (res.status == 304):
        conlen = res.getheader("content-length")
        # print "Conlen? ", conlen
        if not conlen:
            conlen = "<Not found>"
        pingres = pingResult(netloc)
        # print "Pingres? ", pingres
        # geoip = geoIP(netloc)
        # print "Geoip? ", geoip
        return "Content length: " + conlen + " bytes\nping " + pingres
    else:
        return "Error: HTTP Status " + str(res.status)

# findLinks function finds all HTML links in a document
def findLinks(document, fullpath):
    soup = BeautifulSoup(document)
    for a in soup.findAll('a', href=True):
        span = soup.new_tag('span')
        a.replaceWith(span)
        span.insert(0, a)
        span['title'] = getLinkInfo(a['href'], fullpath)
    return str(soup)

if __name__ == '__main__':
    try:
        if len(sys.argv) != 3:
            print "Usage: python " + sys.argv[0] + "[hostname] [port number]"
            sys.exit(1)
        hostname = sys.argv[1]
        portno = int(sys.argv[2])
        
        server = Server(hostname, portno)
        request = server.readFromClient()
        
        client = Client(request, 80)
        client.sendToServer(request)
        resp = client.readFromServer()
        server.sendToClient(resp)

    except KeyboardInterrupt:
        print "Ctrl C - Stopping server"
        sys.exit(1)