# proxy.py
# COMP 112 Project 5
# Lucy Qin and Nate Matthews

import socket
import sys
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
    def __init__(self, host, port):
        self.permhost = host
        print "Permhost: ", self.permhost
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
        return findLinks(resp, self.permhost)

def contentLength(netloc, path):
    conn = httplib.HTTPConnection(netloc)
    conn.request("HEAD", netloc + path)
    res = conn.getresponse()
    return res.getheader("content-length")

def pingResult(netloc):
    try:
        child = pexpect.spawn('ping -c 5 ' + netloc)
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
        print "Connection: ", conn
    except Exception, e:
        raise e
    conn.request("GET", "/csv/" + netloc)
    res = conn.getresponse()
    return res.read()

# findLinks function finds all HTML links in a document
def findLinks(document, hostname):

    # linkstr = "<a href="
    # searchfrom = 0

    soup = BeautifulSoup(document)
    for a in soup.findAll('a'):
        span = soup.new_tag('span')
        a.replaceWith(span)
        span.insert(0, a)
        parsed = urlparse.urlparse(a['href'])
        netloc = parsed.netloc
        if netloc == "":
            netloc = hostname
        conlen = contentLength(netloc, parsed.path)
        pingres = pingResult(netloc)
        geoip = geoIP(netloc)
        span['title'] = conlen + " " + pingres + " " + geoip
    return str(soup)

        # try:
        #     # Index of the first quotation mark after <a href=
        #     startind = document.index(linkstr, searchfrom) + len(linkstr)
        #     if startind == -1: # index() returns -1 in the case of an error
        #         break
        #     # Index of the closing quotation mark for the href value
        #     endind = document.index(document[startind], startind + 1)
        #     if endind == -1: # index() returns -1 in the case of an error
        #         break
        #     # Print the values between the quotation marks
        #     getPageInfo(document[(startind + 1):endind])
        #     # In the next iteration of the loop we start the search after the
        #     # link just processed:
        #     searchfrom = endind + 1
        # # index() throws a ValueError if it cannot find the specificied string:
        # except ValueError:
        #     break

def forwardAddress(request):
    elems = request.split()
    if len(elems) == 0:
        sys.exit("Error: Request does not contain separatable words")
    elif elems[0] != "GET":
        sys.exit("Error: Proxy can only handle HTML GET requests")
    elif elems[3] == "Host:":
        return elems[4]
    else:
        print elems[4], elems[1]
        return elems[1]

if __name__ == '__main__':
    try:
        if len(sys.argv) != 3:
            print "Usage: python " + sys.argv[0] + "[hostname] [port number]"
            sys.exit(1)
        hostname = sys.argv[1]
        portno = int(sys.argv[2])
        
        server = Server(hostname, portno)
        request = server.readFromClient()
        
        client = Client(forwardAddress(request), 80)
        client.sendToServer(request)
        resp = client.readFromServer()
        server.sendToClient(resp)

    except KeyboardInterrupt:
        print "Ctrl C - Stopping server"
        sys.exit(1)