
# proxyproject 
#### COMP112 Networks and Protocols, Assignment #5
Nate Matthews and Lucy Qin

##### Project Description
The proxy listens on a specified port number. If sent an HTTP GET request, the proxy forwards 
the request to its final destination. The proxy then stores the response, parses the HTML document to find each link. The proxy then makes HTTP HEAD requests for each of these links to get a hint about the speed that each page can be accessed. This hint is then embedded to the HTML content so that when a link is hovered on, the information displays in a window. 

The hint is an estimated download speed. This is calculated as:
{Estimated Download Speed} = {Estimated Propagation Delay} + {Estimated Transmission Delay}

where

{Estimated Propation Delay} = {Time when HEAD request is sent}  - {Time when header is received}

and 

{Transmission Delay} = {Content length in bytes (from header)} / {Bandwidth}

Currently the bandwidth we use is simply a constant, based on a reasonable guess, but a future implementation of this would benefit from estimating the bandwidth based on the current machine and network situation.

In previous versions we also included the physical location of the servers of each page using GeoIP and ping results. However this slowed down our program significantly since we were relying on a service called freegeoip, which we noticed was the bottleneck. This information is slightly redundant since they are simply other estimates of propagation delay. To speed up our program, we decided to no longer use the GeoIP and Ping services.




##### Possible Extensions
Currently the proxy only works with websites that are encoded using utf-8. Future versions could work with a variety of encodings.
The proxy only handles one request. Future work could handle multiple requests. 

##### Applications


Times:
1) 2223
2.) 3005
3.) 1137
4.) 1842
5.) 1223

Usage: `python proxy.py [proxy host name] [proxy port number]`






