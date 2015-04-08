import socket
import time
import sys
import select

NUM_CLIENTS = 5
BUFFER_SIZE = 4096

# class Forward:
#     def __init__(self):
#         self.forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
 
#     def start(self, host, port):
#         try:
#             self.forward.connect((host, port))
#             return self.forward
#         except Exception, e:
#             print e
#             return False


class Server:
    def __init__(self, host, port):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
     #   self.server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server.bind((host, port))
        self.server.listen(NUM_CLIENTS)
        print "listening in on port ", port


    def readFromClient(self):
        print "hello"
        cli_sockfd, cli_addr = self.server.accept()
        print cli_addr, "has connected"
        self.data = cli_sockfd.recv(BUFFER_SIZE)
        return self.data

if __name__ == '__main__':
    try:
        if len(sys.argv) != 3:
            print "Please specify port number"
            sys.exit(1)
        hostname = sys.argv[1]
        portno = int(sys.argv[2])
        print hostname, portno
        server = Server(hostname, portno)
        req = server.readFromClient()
        elems = req.split()
        for a in elems:
            print a
        dest = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            dest.connect((elems[4], 80))
            dest.send(req)
            document = dest.recv(BUFFER_SIZE)
        except Exception, e:
            print e

           
    except KeyboardInterrupt:
        print "Ctrl C - Stopping server"
        sys.exit(1)