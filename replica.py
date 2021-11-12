####################
# Course: CSE138
# Date: Fall 2021
# Assignment: 3
# Tommaso Framba
# Eric Yao Huang
# This program implements a distributed KVS Store
# with proper causal delivery property
###################

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import os.path
import json
import requests
import socket
import subprocess
from html.parser import HTMLParser



#setup the server to initalize its address and view as class fields
class http_server:
    def __init__(self, views, address):
        replicaStoreHandler.view = views
        replicaStoreHandler.sock = address
        server = HTTPServer(('', int(address[1])),replicaStoreHandler)
        print('Server running on address ', address)
        server.serve_forever()

# handle requests
class replicaStoreHandler(BaseHTTPRequestHandler):
    keyValueStore = dict()
    view = []
    count = 0
    sock = ""



    # handle post requests
    def do_PUT(self):
        parsed_path = urlparse(self.path).path.split("/")

        #Put request for view
        if len(parsed_path) == 2 and parsed_path[1] == 'view':

            #Get Json Body '{"socket-address":<NEW-REPLICA>}'
            content_len = int(self.headers.get('content-length'))
            body = self.rfile.read(content_len)
            data = json.loads(body)

            #Check if address is in view
            checkAddress = data['socket-address']
            if checkAddress in self.view:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                jsndict = {"result": "already present"}
                jsnrtrn = json.dumps(jsndict)
                self.wfile.write(jsnrtrn.encode("utf8"))
            else:
                print("The check address is not in view send CREATED")


    def do_GET(self):
        parsed_path = urlparse(self.path).path.split("/")

        # Get request for view
        if len(parsed_path) == 2 and parsed_path[1] == 'view':
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            jsndict = {"view": self.view}
            jsnrtrn = json.dumps(jsndict)
            self.wfile.write(jsnrtrn.encode("utf8"))


    def do_DELETE(self):
        parsed_path = urlparse(self.path).path.split("/")

        # Delete request for view
        if len(parsed_path) == 2 and parsed_path[1] == 'view':

            # Get Json Body '{"socket-address":<NEW-REPLICA>}'
            content_len = int(self.headers.get('content-length'))
            body = self.rfile.read(content_len)
            data = json.loads(body)

            # Check if address is in view
            checkAddress = data['socket-address']
            if checkAddress in self.view:
                self.view.remove(checkAddress)
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                jsndict = {"result": "deleted"}
                jsnrtrn = json.dumps(jsndict)
                self.wfile.write(jsnrtrn.encode("utf8"))
            else:
                self.send_response(404)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                jsndict = {"error": "View has no such replica"}
                jsnrtrn = json.dumps(jsndict)
                self.wfile.write(jsnrtrn.encode("utf8"))

# start and run server on specified port
def main():
    #Get -e vars
    address = str(os.environ.get('SOCKET_ADDRESS')).split(':')
    views = str(os.environ.get('VIEW')).split(',')
    server = http_server(views, address)

if __name__ == '__main__':
    main()
