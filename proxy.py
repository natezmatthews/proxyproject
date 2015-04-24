# proxy.py
# COMP 112 Project 5
# Lucy Qin and Nate Matthews


import socket
import sys
import json
import select
import http.client
import re
import time

try: 
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import pexpect

try: 
    from bs4 import BeautifulSoup
except ImportError:
    import beautifulsoup4

NUM_CLIENTS = 1
BUFFER_SIZE = 4096
DOWNLOAD_SPEED = 16250 #bytes per millisecond

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
        self.cli_sockfd.send(data.encode('utf-8'))

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
            print ("Client host: ", host)
            if urlparse(elems[1]).netloc == "":
                self.fullpath = elems[4] + elems[1]
            else:
                self.fullpath = elems[1]
            print ("Client fullpath: ", self.fullpath)
        else:
            host = elems[1]
            print ("Client host: ", host)
            self.fullpath = elems[1]
            print ("Client fullpath: ", self.fullpath)

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.client.connect((host, port))
        except Exception as e:
            raise e

    def sendToServer(self, data):
        self.client.send(data.encode('utf-8'))
    
    def readFromServer(self):
        resp = ''
        while 1:
            read = (self.client.recv(BUFFER_SIZE)).decode('utf-8')
            if len(read) == 0:
                break
            resp += read
        return findLinks(resp, self.fullpath)

# def pingResult(netloc):
#     try:
#         child = pexpect.spawn('ping -c 3 ' + netloc)
#     except Exception as e:
#         raise e
#     while 1:
#         cur = child.readline()
#         if not cur: break
#         prev = cur
#     return prev

# def geoIP(netloc):
#     try:
#         conn = http.client.HTTPConnection("freegeoip.net")
#     except Exception as e:
#         raise e
#     conn.request("GET", "/csv/" + netloc)
#     res = conn.getresponse()
#     return res.read()

def getLinkInfo(href, origuri):
    parsed = urlparse(href)
    print ("Href:",href)
    print ("Origuri:",origuri)
    netloc = parsed.netloc
    print ("Netloc:",netloc)
    if netloc == "":
        # CASE: Relative URI:
        if re.search("^https?://",origuri) == None:
            origuri = "http://" + origuri
        parsed_origuri = urlparse(origuri)
        netloc = parsed_origuri.netloc
        print ("Netloc:",netloc)
        i = (origuri.index(netloc) + len(netloc))
        k = origuri.rindex("/")
        path = parsed.path
        print ("Path:",path)
        # In case the relative URI doesn't have a leading /:
        if path and (path[0] != "/"):
            path = "/" + path
        forreq = origuri[i:k] + path
        print ("Forreq:",forreq)
    else:
        # CASE: Absolute URI:
        i = (href.index(netloc) + len(netloc))
        forreq = href[i:]
        print ("Forreq:",forreq)

    conn = http.client.HTTPConnection(netloc)
    try:
        start = int(round(time.time() * 1000))
        conn.request("HEAD", forreq)
        res = conn.getresponse()
        fin = int(round(time.time() * 1000))
    except Exception as e:
        return "Error: Not a valid link"
    print ("HTTP status: ", res.status) 
    if (res.status == 200) or (res.status == 304):
        conlen = res.getheader("content-length")
        print ("Content length: ", conlen)
        if not conlen:
            conlen = 0

        est = (fin - start) + (int(conlen) / DOWNLOAD_SPEED)
        # pingres = pingResult(netloc)
        # geoip = geoIP(netloc)
        # return ("Content length: " + conlen + " bytes\nping " + pingres.decode('utf-8') + geoip.decode('utf-8'))
        # return "Content length: " + conlen + " bytes\nping " + pingres + geoip
        return ("Download Time Estimate: " + str(round(est,2)) + "ms")
    else:
        return "Error: HTTP Status " + str(res.status)

# findLinks function finds all HTML links in a document
def findLinks(document, fullpath):
    try:
        soup = BeautifulSoup(document)
    except Exception as e:
        print ("Exception: " + str(e))

    head = soup.head
    style = soup.new_tag('style')
    style.append('*, *:before, *:after { -webkit-box-sizing: border-box; -moz-box-sizing:    border-box; box-sizing:         border-box;} body { margin: 0 auto; max-width: 640px; width: 90%; } body, button { font-family: "Helvetica Neue", Arial, sans-serif; } button { font-size: 100%; } a:hover { text-decoration: none; } header, .content, .content p { margin: 4em 0; text-align: center; } [data-tooltip] { position: relative; z-index: 2; cursor: pointer; } [data-tooltip]:before, [data-tooltip]:after {  visibility: hidden; -ms-filter: "progid:DXImageTransform.Microsoft.Alpha(Opacity=0)"; filter: progid:DXImageTransform.Microsoft.Alpha(Opacity=0); opacity: 0; pointer-events: none; } [data-tooltip]:before { position: absolute; bottom: 150%; left: 50%; margin-bottom: 5px; margin-left: -80px; padding: 7px; width: 160px; -webkit-border-radius: 3px; -moz-border-radius:    3px; border-radius: 3px; background-color: #000; background-color: hsla(0, 0%, 20%, 0.9); color: #fff; content: attr(data-tooltip); text-align: center; font-size: 14px; line-height: 1.2; } [data-tooltip]:after { position: absolute; bottom: 150%; left: 50%; margin-left: -5px; width: 0; border-top: 5px solid #000; border-top: 5px solid hsla(0, 0%, 20%, 0.9); border-right: 5px solid transparent; border-left: 5px solid transparent; content: " "; font-size: 0; line-height: 0; }  [data-tooltip]:hover:before, [data-tooltip]:hover:after { visibility: visible; -ms-filter: "progid:DXImageTransform.Microsoft.Alpha(Opacity=100)"; filter: progid:DXImageTransform.Microsoft.Alpha(Opacity=100); opacity: 1; }')
    # head.append(style)

    for a in soup.findAll('a', href=True):
        a['title'] = getLinkInfo(a['href'], fullpath)
        # span = soup.new_tag('span')
        # a.replaceWith(span)
        # span.insert(0, a)
        # span['title'] = getLinkInfo(a['href'], fullpath)
        # span['class'] = 'tooltip'
    return str(soup)

if __name__ == '__main__':
    try:
        if len(sys.argv) != 3:
            print ("Usage: python " + sys.argv[0] + "[hostname] [port number]")
            sys.exit(1)
        hostname = sys.argv[1]
        portno = int(sys.argv[2])
        
        server = Server(hostname, portno)
        request = (server.readFromClient()).decode('utf-8')
        
        client = Client(request, 80)
        client.sendToServer(request)
        resp = client.readFromServer()
        server.sendToClient(resp)

    except KeyboardInterrupt:
        print ("Ctrl C - Stopping server")
        sys.exit(1)