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
        replicaStoreHandler.startUpBroadcast(replicaStoreHandler)
        server = HTTPServer(('', int(address[1])),replicaStoreHandler)
        print('Server running on address ', address)
        server.serve_forever()

# handle requests
class replicaStoreHandler(BaseHTTPRequestHandler):
    keyValueStore = dict()
    view = []
    metadata = []
    count = 0
    sock = ""

    # at startup, put yourself to everyone's view
    def startUpBroadcast(self):
        for i in self.view:
            #add metadata slot for each replica
            self.metadata.append(0)

            #Don't check our own socket address
            if i == os.environ.get('SOCKET_ADDRESS'):
                continue

            #Check if the view is up
            host = i.split(":")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((host[0], int(host[1])))
            if result == 0:
                sock.close()

                #send a put /view to each view
                url = "http://" + i + "/view"
                jsndict = {"socket-address": os.environ.get('SOCKET_ADDRESS')}
                data = json.dumps(jsndict)
                response = requests.put(url, data=data, timeout=2.50)
                print("\nresponse is: ")
                print(response)
            else:
                print(i + " is not up yet")

    # handle post requests
    def do_PUT(self):
        parsed_path = urlparse(self.path).path.split("/")

        #Put request for view
        if len(parsed_path) == 2 and parsed_path[1] == 'view':

            #Get Json Body '{"socket-address":<NEW-REPLICA>}'
            content_len = int(self.headers.get('content-length'))
            body = self.rfile.read(content_len)
            data = json.loads(body)
            #print("What is data: ", data)

            #Check if address is in view
            checkAddress = data['socket-address']
            #print("Check address: ", checkAddress)
            if checkAddress in self.view:
                self.send_response(200)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                jsndict = {"result": "already present"}
                jsnrtrn = json.dumps(jsndict)
                self.wfile.write(jsnrtrn.encode("utf8"))
                print("address in self view")
            else:
                self.view.append(checkAddress)
                self.send_response(201)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                self.metadata.append(0) #add a new slot for new replica
                jsndict = {"result": "added"}
                jsnrtrn = json.dumps(jsndict)
                self.wfile.write(jsnrtrn.encode("utf8"))
                print("address not in self view")

        #Put request for kvs
        #TODO: response 503 Service Unavailable logic and response
        if len(parsed_path) == 2 and parsed_path[1] == 'kvs': parsed_path.append("")
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':
                # Get Json body {"value": <value>}
                content_len = int(self.headers.get('content-length'))
                body = self.rfile.read(content_len)
                data = json.loads(body)
                print(data)

                # 400 BAD REQUEST KEY TOO LONG
                if len(parsed_path[2]) > 50:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = {"error": "Key is too long"}
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))
                # 400 BAD REQUEST NO VALUE SPECIFIED
                elif 'value' not in data:
                    self.send_response(400)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = {"error": "PUT request does not specify a value"}
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))
                elif 'value' in data:
                    ##200 OK
                    if parsed_path[2] in self.keyValueStore:
                        self.keyValueStore[parsed_path[2]] = data['value']
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        jsndict = {"result": "replaced"}
                        jsnrtrn = json.dumps(jsndict)
                        self.wfile.write(jsnrtrn.encode("utf8"))
                        
                    ##201 CREATED
                    else:
                        self.send_response(201)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        jsndict = {"result": "created"}
                        jsnrtrn = json.dumps(jsndict)
                        self.wfile.write(jsnrtrn.encode("utf8"))
                        self.keyValueStore[parsed_path[2]] = data['value']



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

        #Get request for kvs
        #TODO: response 503 service unavailable
        if len(parsed_path) == 2 and parsed_path[1] == 'kvs': parsed_path.append("")  # Handle as if it was empty string
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':

                # If key exists #200 OK else #404 Not Found
                if parsed_path[2] in self.keyValueStore:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = { "result": "found", "value": self.keyValueStore[parsed_path[2]] }
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = {"error": "Key does not exist"}
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

        #Delete request for kvs
        #TODO: 503 service unavailable error causal dependiecies not satisfied
        if len(parsed_path) == 2 and parsed_path[1] == 'kvs': parsed_path.append("")  # Handle as if it was empty string
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':
                if parsed_path[2] in self.keyValueStore:
                    #TODO 200
                    print("200")
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = {"error": "Key does not exist"}
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
