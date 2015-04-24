# proxy.py
# COMP 112 Project 5
# Lucy Qin and Nate Matthews


import socket
import sys
import json
import select
import http.client
import re

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

def pingResult(netloc):
    try:
        child = pexpect.spawn('ping -c 3 ' + netloc)
    except Exception as e:
        raise e
    while 1:
        cur = child.readline()
        if not cur: break
        prev = cur
    return prev

def geoIP(netloc):
    try:
        conn = http.client.HTTPConnection("freegeoip.net")
    except Exception as e:
        raise e
    conn.request("GET", "/csv/" + netloc)
    res = conn.getresponse()
    return res.read()

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
        conn.request("HEAD", forreq)
        res = conn.getresponse()
    except Exception as e:
        return "Error: Not a valid link"
    print ("HTTP status: ", res.status) 
    if (res.status == 200) or (res.status == 304):
        conlen = res.getheader("content-length")
        print ("Content length: ", conlen)
        if not conlen:
            conlen = "<Not found>"

        pingres = pingResult(netloc)
        # geoip = geoIP(netloc)

        return ("Content length: " + conlen + " bytes\nping " + pingres.decode('utf-8'))

        # return "Content length: " + conlen + " bytes\nping " + pingres + geoip
    else:
        return "Error: HTTP Status " + str(res.status)

# findLinks function finds all HTML links in a document
def findLinks(document, fullpath):
    soup = BeautifulSoup(document)

    head = soup.head


    # css_link = soup.new_tag('link')
    # css_link['rel'] = 'stylesheet'
    # css_link['href']= '//code.jquery.com/ui/1.11.4/themes/smoothness/jquery-ui.css'
    # head.append(css_link)

    # script_1 = soup.new_tag('script')
    # script_1['src'] = '//code.jquery.com/jquery-1.10.2.js'
    # head.append(script_1)


    # script_2 = soup.new_tag('script')

    # head.append(script_2)




    # script_2 = soup.new_tag('script')
    # script_2['src'] = '//code.jquery.com/ui/1.11.4/jquery-ui.js'

    # script_3 = soup.new_tag('script')
    # script_3['src'] =  '$(function() { $(a).tooltip();});'

    # style = soup.new_tag('style')
    # style.append('.tooltipster-default { border-radius: 5px;  border: 2px solid #000; background: #4c4c4c; color: #fff; } .tooltipster-default .tooltipster-content { font-family: Arial, sans-serif; font-size: 14px; line-height: 16px; padding: 8px 10px; overflow: hidden;} .tooltipster-default .tooltipster-arrow .tooltipster-arrow-border { }/* This next selector defines the color of the border on the outside of the arrow. This will automatically match the color and size of the border set on the main tooltip styles. Set display: none; if you would like a border around the tooltip but no border around the arrow *//* This is the base styling required to make all Tooltipsters work */.tooltipster-base { padding: 0; font-size: 0; line-height: 0; position: absolute; left: 0; top: 0; z-index: 9999999; pointer-events: none; width: auto; overflow: visible;}.tooltipster-base .tooltipster-content { overflow: hidden; }.tooltipster-arrow { display: block; text-align: center; width: 100%; height: 100%; position: absolute; top: 0; left: 0; z-index: -1;}.tooltipster-arrow span, .tooltipster-arrow-border { display: block; width: 0;  height: 0; position: absolute; }.tooltipster-arrow-top span, .tooltipster-arrow-top-right span, .tooltipster-arrow-top-left span { border-left: 8px solid transparent !important; border-right: 8px solid transparent !important; border-top: 8px solid; bottom: -7px; }.tooltipster-arrow-top .tooltipster-arrow-border, .tooltipster-arrow-top-right .tooltipster-arrow-border, .tooltipster-arrow-top-left .tooltipster-arrow-border { border-left: 9px solid transparent !important; border-right: 9px solid transparent !important; border-top: 9px solid; bottom: -7px;}.tooltipster-arrow-bottom span, .tooltipster-arrow-bottom-right span, .tooltipster-arrow-bottom-left span { border-left: 8px solid transparent !important; border-right: 8px solid transparent !important; border-bottom: 8px solid; top: -7px;}.tooltipster-arrow-bottom .tooltipster-arrow-border, .tooltipster-arrow-bottom-right .tooltipster-arrow-border, .tooltipster-arrow-bottom-left .tooltipster-arrow-border { border-left: 9px solid transparent !important; border-right: 9px solid transparent !important; border-bottom: 9px solid; top: -7px;}.tooltipster-arrow-top span, .tooltipster-arrow-top .tooltipster-arrow-border, .tooltipster-arrow-bottom span, .tooltipster-arrow-bottom .tooltipster-arrow-border { left: 0; right: 0; margin: 0 auto;}.tooltipster-arrow-top-left span, .tooltipster-arrow-bottom-left span { left: 6px; }.tooltipster-arrow-top-left .tooltipster-arrow-border, .tooltipster-arrow-bottom-left .tooltipster-arrow-border { left: 5px;}.tooltipster-arrow-top-right span,  .tooltipster-arrow-bottom-right span { right: 6px;}.tooltipster-arrow-top-right .tooltipster-arrow-border, .tooltipster-arrow-bottom-right .tooltipster-arrow-border { right: 5px;}.tooltipster-arrow-left span, .tooltipster-arrow-left .tooltipster-arrow-border { border-top: 8px solid transparent !important; border-bottom: 8px solid transparent !important;  border-left: 8px solid; top: 50%; margin-top: -7px; right: -7px;}.tooltipster-arrow-left .tooltipster-arrow-border { border-top: 9px solid transparent !important; border-bottom: 9px solid transparent !important;  border-left: 9px solid; margin-top: -8px;}.tooltipster-arrow-right span, .tooltipster-arrow-right .tooltipster-arrow-border { border-top: 8px solid transparent !important; border-bottom: 8px solid transparent !important;  border-right: 8px solid; top: 50%; margin-top: -7px; left: -7px;}.tooltipster-arrow-right .tooltipster-arrow-border { border-top: 9px solid transparent !important; border-bottom: 9px solid transparent !important;  border-right: 9px solid; margin-top: -8px;}/* Some CSS magic for the awesome animations - feel free to make your own custom animations and reference it in your Tooltipster settings! */.tooltipster-fade { opacity: 0; -webkit-transition-property: opacity; -moz-transition-property: opacity; -o-transition-property: opacity; -ms-transition-property: opacity; transition-property: opacity;}.tooltipster-fade-show { opacity: 1;}.tooltipster-grow { -webkit-transform: scale(0,0); -moz-transform: scale(0,0); -o-transform: scale(0,0); -ms-transform: scale(0,0); transform: scale(0,0); -webkit-transition-property: -webkit-transform; -moz-transition-property: -moz-transform; -o-transition-property: -o-transform; -ms-transition-property: -ms-transform; transition-property: transform; -webkit-backface-visibility: hidden;}.tooltipster-grow-show { -webkit-transform: scale(1,1); -moz-transform: scale(1,1); -o-transform: scale(1,1); -ms-transform: scale(1,1); transform: scale(1,1); -webkit-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1); -webkit-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15);  -moz-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15);  -ms-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15);  -o-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15);  transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15);}.tooltipster-swing { opacity: 0; -webkit-transform: rotateZ(4deg); -moz-transform: rotateZ(4deg); -o-transform: rotateZ(4deg); -ms-transform: rotateZ(4deg); transform: rotateZ(4deg); -webkit-transition-property: -webkit-transform, opacity; -moz-transition-property: -moz-transform; -o-transition-property: -o-transform; -ms-transition-property: -ms-transform; transition-property: transform;}.tooltipster-swing-show { opacity: 1; -webkit-transform: rotateZ(0deg); -moz-transform: rotateZ(0deg); -o-transform: rotateZ(0deg); -ms-transform: rotateZ(0deg); transform: rotateZ(0deg); -webkit-transition-timing-function: cubic-bezier(0.230, 0.635, 0.495, 1); -webkit-transition-timing-function: cubic-bezier(0.230, 0.635, 0.495, 2.4);  -moz-transition-timing-function: cubic-bezier(0.230, 0.635, 0.495, 2.4);  -ms-transition-timing-function: cubic-bezier(0.230, 0.635, 0.495, 2.4);  -o-transition-timing-function: cubic-bezier(0.230, 0.635, 0.495, 2.4);  transition-timing-function: cubic-bezier(0.230, 0.635, 0.495, 2.4);}.tooltipster-fall { top: 0; -webkit-transition-property: top; -moz-transition-property: top; -o-transition-property: top; -ms-transition-property: top; transition-property: top; -webkit-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1); -webkit-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15);  -moz-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15);  -ms-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15);  -o-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15);  transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15); }.tooltipster-fall-show {}.tooltipster-fall.tooltipster-dying { -webkit-transition-property: all; -moz-transition-property: all; -o-transition-property: all; -ms-transition-property: all; transition-property: all; top: 0px !important; opacity: 0;}.tooltipster-slide { left: -40px; -webkit-transition-property: left; -moz-transition-property: left; -o-transition-property: left; -ms-transition-property: left; transition-property: left; -webkit-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1); -webkit-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15);  -moz-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15);  -ms-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15);  -o-transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15);  transition-timing-function: cubic-bezier(0.175, 0.885, 0.320, 1.15);}.tooltipster-slide.tooltipster-slide-show {}.tooltipster-slide.tooltipster-dying { -webkit-transition-property: all; -moz-transition-property: all; -o-transition-property: all; -ms-transition-property: all; transition-property: all; left: 0px !important; opacity: 0;}/* CSS transition for when contenting is changing in a tooltip that is still open. The only properties that will NOT transition are: width, height, top, and left */.tooltipster-content-changing { opacity: 0.5; -webkit-transform: scale(1.1, 1.1); -moz-transform: scale(1.1, 1.1); -o-transform: scale(1.1, 1.1); -ms-transform: scale(1.1, 1.1); transform: scale(1.1, 1.1);}')
    # # style.append('label {display: inline-block; width: 5em;}')
    # head.append(style)

    # style = soup.new_tag('style')
    # style.append()


    style = soup.new_tag('style')
    style.append('*, *:before, *:after { -webkit-box-sizing: border-box; -moz-box-sizing:    border-box; box-sizing:         border-box;} body { margin: 0 auto; max-width: 640px; width: 90%; } body, button { font-family: "Helvetica Neue", Arial, sans-serif; } button { font-size: 100%; } a:hover { text-decoration: none; } header, .content, .content p { margin: 4em 0; text-align: center; } [data-tooltip] { position: relative; z-index: 2; cursor: pointer; } [data-tooltip]:before, [data-tooltip]:after {  visibility: hidden; -ms-filter: "progid:DXImageTransform.Microsoft.Alpha(Opacity=0)"; filter: progid:DXImageTransform.Microsoft.Alpha(Opacity=0); opacity: 0; pointer-events: none; } [data-tooltip]:before { position: absolute; bottom: 150%; left: 50%; margin-bottom: 5px; margin-left: -80px; padding: 7px; width: 160px; -webkit-border-radius: 3px; -moz-border-radius:    3px; border-radius: 3px; background-color: #000; background-color: hsla(0, 0%, 20%, 0.9); color: #fff; content: attr(data-tooltip); text-align: center; font-size: 14px; line-height: 1.2; } [data-tooltip]:after { position: absolute; bottom: 150%; left: 50%; margin-left: -5px; width: 0; border-top: 5px solid #000; border-top: 5px solid hsla(0, 0%, 20%, 0.9); border-right: 5px solid transparent; border-left: 5px solid transparent; content: " "; font-size: 0; line-height: 0; }  [data-tooltip]:hover:before, [data-tooltip]:hover:after { visibility: visible; -ms-filter: "progid:DXImageTransform.Microsoft.Alpha(Opacity=100)"; filter: progid:DXImageTransform.Microsoft.Alpha(Opacity=100); opacity: 1; }')

    # style.append('.wrapper { text-transform: uppercase; background: #ececec; color: #555; cursor: help; font-family: "Gill Sans", Impact, sans-serif; font-size: 20px; margin: 100px 75px 10px 75px; padding: 15px 20px; position: relative; text-align: center; width: 200px; -webkit-transform: translateZ(0); /* webkit flicker fix */ -webkit-font-smoothing: antialiased; /* webkit text rendering fix */ } .wrapper .tooltip { background: #1496bb; bottom: 100%; color: #fff; display: block; left: -25px; margin-bottom: 15px; opacity: 0; padding: 20px; pointer-events: none; position: absolute; width: 100%; -webkit-transform: translateY(10px); -moz-transform: translateY(10px); -ms-transform: translateY(10px); -o-transform: translateY(10px); transform: translateY(10px); -webkit-transition: all .25s ease-out; -moz-transition: all .25s ease-out; -ms-transition: all .25s ease-out; -o-transition: all .25s ease-out; transition: all .25s ease-out; -webkit-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28); -moz-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28); -ms-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28); -o-box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28); box-shadow: 2px 2px 6px rgba(0, 0, 0, 0.28); }  .wrapper .tooltip:before { bottom: -20px; content: " "; display: block; height: 20px; left: 0; position: absolute; width: 100%; .wrapper .tooltip:after { border-left: solid transparent 10px; border-right: solid transparent 10px; border-top: solid #1496bb 10px; bottom: -10px; content: " "; height: 0; left: 50%; margin-left: -13px; position: absolute; width: 0; } .wrapper:hover .tooltip { opacity: 1; pointer-events: auto; -webkit-transform: translateY(0px); -moz-transform: translateY(0px); -ms-transform: translateY(0px); -o-transform: translateY(0px); transform: translateY(0px); } .lte8 .wrapper .tooltip { display: none; } .lte8 .wrapper:hover .tooltip { display: block; }')

    head.append(style)




    for a in soup.findAll('a', href=True):
        a['data-tooltip'] = getLinkInfo(a['href'], fullpath)
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