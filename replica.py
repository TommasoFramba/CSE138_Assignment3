####################
# Course: CSE138
# Date: Fall 2021
# Assignment: 2
# Tommaso Framba
# Eric Yao Huang
# This program implements a simple HTTP interface with specified
# responses to GET and PUT and DELETE requests.
###################

from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import os.path
import json
import requests
import socket
import subprocess
from html.parser import HTMLParser


# handle requests
class replicaStoreHandler(BaseHTTPRequestHandler):
    keyValueStore = dict()
    view = []
    count = 0

    def setView(self, view):
        self.view = view

    def do_GET(self):
        print("GET!")

        if self.count != 1:
            response = requests.get("http://10.10.0.2:8090", timeout=2.50)
            self.count = 1

# start and run server on port 8090
def main():
    #Get -e vars
    address = str(os.environ.get('SOCKET_ADDRESS')).split(':')
    views = os.environ.get('VIEW')
    server = HTTPServer((address[0], int(address[1])), replicaStoreHandler)
    print('Server running on address ', address)
    server.serve_forever()


if __name__ == '__main__':
    main()
