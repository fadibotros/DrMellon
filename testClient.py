import urllib
import httplib
import socket
import json


hostip = 'ec2-54-175-235-18.compute-1.amazonaws.com'
port = 8080

data = [1,2]

jsonStr = json.dumps(data)
headers = {"Content-type": "application/json"}
# headers = {"Content-type": "application/json"}
conn = httplib.HTTPConnection(hostip + ":" + str(port))
conn.request("POST","/",jsonStr, headers)
response = conn.getresponse()

print response.read()