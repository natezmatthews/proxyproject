import sys
import urllib2

req = urllib2.Request(sys.argv[1])
response = urllib2.urlopen(req)
the_page = response.read()
print the_page