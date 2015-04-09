# proxyproject 
#### COMP112 Networks and Protocols, Assignment #5
Nate Matthews and Lucy Qin

##### Project Description
The proxy listens on a specified port number. If sent an HTTP GET request, the proxy forwards 
the request to its final destination. The proxy then stores the response, and for each HTML
link found in the response, the proxy adds a window that will appear on mouseover. These windows
will contain hints as to which webpages are likely to be faster/slower to download. 

The hints will be at minimum:

1. An average round-trip-time calculated by the proxy
2. The size of the webpage

Other hints we may implement:

1. The physical location of the destination server
2. The availability of the webpage in a cache in the proxy

##### Current Progress
The proxy currently forwards the first GET request it gets, stores the response,
prints out whatever HTML links it finds in the response, and then forwards the response to the client.

Usage: `python proxy.py [proxy host name] [proxy port number]`





