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

    def setView(self, view):
        self.view = view

    def do_GET(self):
        print("GET!")


# start and run server on port 8090
def main():
    #Get -e vars
    address = str(os.environ.get('SOCKET_ADDRESS')).split(':')
    views = os.environ.get('VIEW')
    server = HTTPServer(('', 8090), replicaStoreHandler)
    print('Server running on address ', address)
    server.serve_forever()


if __name__ == '__main__':
    main()
