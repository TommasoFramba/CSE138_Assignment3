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

    def setView(self, view):
        self.view = view

    # handle post requests
    def do_PUT(self):
        parsed_path = urlparse(self.path).path.split("/")
        if len(parsed_path) == 2 and parsed_path[1] == 'view':
            print("My sock: ", self.sock)
            print("My view: ", self.view)




    def do_GET(self):
        print("GET!")

        parsed_path = self.path
        url = "http://" + os.environ.get('SOCKET_ADDRESS')
        host = str(os.environ.get('SOCKET_ADDRESS')).split(":")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex((host[0], int(host[1])))
        print(result)

        sock.close()


# start and run server on port 8090
def main():
    #Get -e vars
    address = str(os.environ.get('SOCKET_ADDRESS')).split(':')
    views = os.environ.get('VIEW')
    server = http_server(views, address)

if __name__ == '__main__':
    main()
