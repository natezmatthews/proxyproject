# proxy.py
# COMP 112 Project 5
# Lucy Qin and Nate Matthews

import socket
import sys
import re
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
            if urlparse.urlparse(elems[1]).netloc == "":
                self.fullpath = elems[4] + elems[1]
            else:
                self.fullpath = elems[1]
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

def getLinkInfo(href, origuri):
    parsed = urlparse.urlparse(href)
    print "Href:",href
    print "Origuri:",origuri
    netloc = parsed.netloc
    print "Netloc:",netloc
    if netloc == "":
        # CASE: Relative URI:
        if re.search("^https?://",origuri) == None:
            origuri = "http://" + origuri
        parsed_origuri = urlparse.urlparse(origuri)
        netloc = parsed_origuri.netloc
        print "Netloc:",netloc
        i = (origuri.index(netloc) + len(netloc))
        k = origuri.rindex("/")
        path = parsed.path
        print "Path:",path
        # In case the relative URI doesn't have a leading /:
        if path and (path[0] != "/"):
            path = "/" + path
        forreq = origuri[i:k] + path
        print "Forreq:",forreq
    else:
        # CASE: Absolute URI:
        i = (href.index(netloc) + len(netloc))
        forreq = href[i:]
        print "Forreq:",forreq

    conn = httplib.HTTPConnection(netloc)
    try:
        conn.request("HEAD", forreq)
        res = conn.getresponse()
    except Exception, e:
        return "Error: Not a valid link"
    if (res.status == 200) or (res.status == 304):
        conlen = res.getheader("content-length")
        if not conlen:
            conlen = "<Not found>"
        pingres = pingResult(netloc)
        geoip = geoIP(netloc)
        return "Content length: " + conlen + " bytes\nping " + pingres + geoip
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