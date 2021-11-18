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
        replicaStoreHandler.alwaysView = views.copy()
        replicaStoreHandler.sock = address
        replicaStoreHandler.startUpBroadcast(replicaStoreHandler)
        server = HTTPServer(('', int(address[1])),replicaStoreHandler)
        print('Server running on address ', address)
        server.serve_forever()

# handle requests
class replicaStoreHandler(BaseHTTPRequestHandler):
    keyValueStore = dict()
    view = []
    alwaysView = []
    metadata = []
    sock = ""

    def incrementMetadata(self, index):
        self.metadata[index] = self.metadata[index] + 1
        print("Metadata: ", self.metadata)

    def return503(self):
        self.send_response(503)
        self.send_header("Content-type", "application/json")
        self.end_headers()
        jsndict = {"error": "Causal dependencies not satisfied; try again later"}
        jsnrtrn = json.dumps(jsndict)
        self.wfile.write(jsnrtrn.encode("utf8"))  
        
    # When a new replica is started broadcast its view to
    # other replicas so they can add to their own view
    def startUpBroadcast(self):
        #Do we need to get key value store and state
        getKVSFlag = False
        getStateFlag = False

        #initialize our metadata
        self.metadata = [0] * len(self.view)

        #For every view send a put view
        for i in self.view:

            #Don't send to our own socket address
            if i == os.environ.get('SOCKET_ADDRESS'):
                continue

            #Check if the view is up
            host = i.split(":")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            print(host)
            result = sock.connect_ex((host[0], int(host[1])))
            if result == 0:
                sock.close()

                #Send a put /view to the view
                url = "http://" + i + "/view"
                jsndict = {"socket-address": os.environ.get('SOCKET_ADDRESS')}

                jsndict['increment-metadata'] = True

                #If we need to get the key value store and state
                if not getKVSFlag:
                    print("We need to get kvs asking ", i)
                    jsndict['getKVS'] = True
                    jsndict['getState'] = True

                #Get back the json data from the view we requested
                data = json.dumps(jsndict)
                response = requests.put(url, data=data, timeout=2.50)
                dataFromResponse = response.json()

                #Put the key value store from view into our key value store
                if not getKVSFlag:
                    self.keyValueStore = dataFromResponse['kvs']
                    print(self.keyValueStore)
                    getKVSFlag = True

                #Put the state from view into our own state
                if not getStateFlag:
                    self.metadata = dataFromResponse['state']
                    print(self.metadata)
                    getStateFlag = True

            else:
                #View is not up
                print(i + " is not up")



    # handle PUT requests
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

                #If we need to get KVS pass it back in response
                if 'getKVS' in data:
                    jsndict['kvs'] = self.keyValueStore
                    jsndict['state'] = self.metadata
                jsnrtrn = json.dumps(jsndict)
                self.wfile.write(jsnrtrn.encode("utf8"))

            else:
                if checkAddress not in self.alwaysView:
                    self.alwaysView.append(checkAddress)
                    self.metadata.append(0)
                    print("my alwaysView: ", self.alwaysView)
                    print("my new metadata: ", self.metadata)
                self.view.append(checkAddress)

                self.send_response(201)
                self.send_header("Content-type", "application/json")
                self.end_headers()
                jsndict = {"result": "added"}





                # If we need to get KVS pass it back in response
                if 'getKVS' in data:
                    jsndict['kvs'] = self.keyValueStore
                    jsndict['state'] = self.metadata
                jsnrtrn = json.dumps(jsndict)
                self.wfile.write(jsnrtrn.encode("utf8"))

        #Put request for kvs
        if len(parsed_path) == 2 and parsed_path[1] == 'kvs': parsed_path.append("")
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':

                # Get Json body
                content_len = int(self.headers.get('content-length'))
                body = self.rfile.read(content_len)
                data = json.loads(body)
                print("Json data from rqst: ", data)

                #Check for 503
                causal = data['causal-metadata']
                if causal != None:
                    print("We have causal metadata")
                    socker = str(self.client_address[0]) + ":8090"
                    flag503 = False
                    if socker not in self.view:
                        print("CLIENT REQUEST CHECKING FOR CAUSAL METADATA")
                        indexOfOurSock = self.alwaysView.index(os.environ.get('SOCKET_ADDRESS'))
                        print("Causal: ", causal)
                        print("OurMetadata: ", self.metadata)
                        print("index of our sock: ", indexOfOurSock)
                        if len(self.metadata) < len(causal): self.metadata.append(0)
                        elif len(self.metadata) > len(causal): causal.append(0)
                        for i in range(0, len(self.metadata)):
                            if self.metadata[i] != causal[i]:
                                flag503 = True
                    else:
                        print("Replica request checking for causal metadata")
                        indexOfClientSock = self.alwaysView.index(socker)
                        print("Causal: ", causal)
                        print("OurMetadata: ", self.metadata)
                        print("index of our sock: ", indexOfClientSock)
                        if len(self.metadata) < len(causal): self.metadata.append(0)
                        elif len(self.metadata) > len(causal): causal.append(0)
                        for i in range(0, len(self.metadata)):
                            if self.metadata[i] != causal[i]:
                                flag503 = True

                    if flag503:
                        self.send_response(503)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        jsndict = {"error": "Causal dependencies not satisfied; try again later"}
                        jsnrtrn = json.dumps(jsndict)
                        self.wfile.write(jsnrtrn.encode("utf8"))
                        return

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
                        # Store the keyvalue pair
                        self.keyValueStore[parsed_path[2]] = data['value']

                        # replica broadcasts write to all the other replicas
                        # update our own metadata
                        if 'replica' not in data:
                            self.broadCastKVS(parsed_path[2], data['value'], True)
                            index = self.alwaysView.index(os.environ.get('SOCKET_ADDRESS'))
                            self.metadata[index] = self.metadata[index] + 1
                            print("Metadata ", self.metadata)
                        else:
                            index = self.alwaysView.index(data['sock'])
                            self.metadata[index] = self.metadata[index] + 1
                            print("Metadata ", self.metadata)

                        #Send back response
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        jsndict = {"result": "updated", "causal-metadata": self.metadata}
                        jsnrtrn = json.dumps(jsndict)
                        self.wfile.write(jsnrtrn.encode("utf8"))

                    ##201 CREATED
                    else:
                        #Store the keyvalue pair
                        self.keyValueStore[parsed_path[2]] = data['value']

                        # replica broadcasts write to all the other replicas
                        # update our own metadata
                        if 'replica' not in data:
                            self.broadCastKVS(parsed_path[2], data['value'], True)
                            index = self.alwaysView.index(os.environ.get('SOCKET_ADDRESS'))
                            self.metadata[index] = self.metadata[index] + 1
                            print("Metadata ", self.metadata)
                        else:
                            index = self.alwaysView.index(data['sock'])
                            self.metadata[index] = self.metadata[index] + 1
                            print("Metadata ", self.metadata)

                        #Send back response
                        self.send_response(201)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        jsndict = {"result": "created", "causal-metadata": self.metadata}
                        jsnrtrn = json.dumps(jsndict)
                        self.wfile.write(jsnrtrn.encode("utf8"))

    #If there are dead views delete them
    def deleteDeadViews(self, deleteThis):
        print("Our view ", self.view)
        print("Delete this ", deleteThis)

        #for all views in our view that are not to be deleted
        viewAppended = [x for x in self.view if x not in deleteThis]
        for i in viewAppended:
            # Don't send to our own address
            if i == os.environ.get('SOCKET_ADDRESS'):
                for x in deleteThis:
                    print("Deleting on our own view: ", x)
                    self.view.remove(x)
                continue

            #On other addresses delete this view
            for x in deleteThis:
                print("Deleting ", x, " on ", i)
                url = "http://" + i + "/view"
                jsndict = {"socket-address": x}
                data = json.dumps(jsndict)
                response = requests.delete(url, data=data, timeout=5)
                print("\nresponse is: ")
                print(response)
        print("Our new view ", self.view)

    #Broadcast a put or delete to the KVS
    def broadCastKVS(self, key, value, putOrDelete):
        deleteThese = []
        for i in self.view:
            #Don't send to our own address
            if i == os.environ.get('SOCKET_ADDRESS'):
                continue

            # Check if the view is up
            host = i.split(":")
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(5)
            result = sock.connect_ex((host[0], int(host[1])))

            if result == 0:
                sock.close()

                if putOrDelete:
                    # send a put /kvs/value to each view
                    url = "http://" + i + "/kvs/" + key
                    jsndict = {"value": value,
                               "replica": True,
                               "causal-metadata": self.metadata,
                               "sock": os.environ.get('SOCKET_ADDRESS')}
                    data = json.dumps(jsndict)
                    response = requests.put(url, data=data, timeout=5)
                    print("\nresponse is: ")
                    print(response)
                else:
                    # send a delete /kvs/value to each view
                    url = "http://" + i + "/kvs/" + key
                    jsndict = {"replica": True,
                               "causal-metadata": self.metadata,
                               "sock": os.environ.get('SOCKET_ADDRESS')}
                    data = json.dumps(jsndict)
                    response = requests.delete(url, data=data, timeout=5)
                    print("\nresponse is: ")
                    print(response)
            else:
                print("One is down delete it!")
                deleteThese.append(i)

        #Delete all dead views
        self.deleteDeadViews(deleteThese)

    #Handle get requests
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
        if len(parsed_path) == 2 and parsed_path[1] == 'kvs': parsed_path.append("")  # Handle as if it was empty string
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':

                # Get Json body {"causal-metadata": <V>}
                content_len = int(self.headers.get('content-length'))
                body = self.rfile.read(content_len)
                data = json.loads(body)
                print("Json data from rqst: ", data)

                # If key exists #200 OK else #404 Not Found
                if parsed_path[2] in self.keyValueStore:
                    # Check causal metadata
                    causal = data['causal-metadata']
                    if causal != None:
                        print("We have causal metadata")
                        socker = str(self.client_address[0]) + ":8090"
                        flag503 = False
                        if socker not in self.view:
                            print("CLIENT REQUEST CHECKING FOR CAUSAL METADATA")
                            indexOfOurSock = self.alwaysView.index(os.environ.get('SOCKET_ADDRESS'))
                            print("Causal: ", causal)
                            print("OurMetadata: ", self.metadata)
                            print("index of our sock: ", indexOfOurSock)
                            if len(self.metadata) < len(causal):
                                self.metadata.append(0)
                            elif len(self.metadata) > len(causal):
                                causal.append(0)
                            for i in range(0,len(self.metadata)):
                                if self.metadata[i] != causal[i]:
                                    flag503 = True
                        else:
                            print("Replica request checking for causal metadata")
                            indexOfClientSock = self.alwaysView.index(socker)
                            print("Causal: ", causal)
                            print("OurMetadata: ", self.metadata)
                            print("index of our sock: ", indexOfClientSock)
                            if len(self.metadata) < len(causal):
                                self.metadata.append(0)
                            elif len(self.metadata) > len(causal):
                                causal.append(0)
                            for i in range(0, len(self.metadata)):
                                if self.metadata[i] != causal[i]:
                                    flag503 = True

                        if flag503:
                            self.send_response(503)
                            self.send_header("Content-type", "application/json")
                            self.end_headers()
                            jsndict = {"error": "Causal dependencies not satisfied; try again later"}
                            jsnrtrn = json.dumps(jsndict)
                            self.wfile.write(jsnrtrn.encode("utf8"))
                            return

                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = {"result": "found", "value": self.keyValueStore[parsed_path[2]],
                               "causal-metadata": self.metadata}
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))

                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = {"error": "Key does not exist"}
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))

    #Handle delete requests
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
                indexOf = self.alwaysView.index(checkAddress)
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
        if len(parsed_path) == 2 and parsed_path[1] == 'kvs': parsed_path.append("")  # Handle as if it was empty string
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':
                if parsed_path[2] in self.keyValueStore:

                    # Get Json Body '{"socket-address":<NEW-REPLICA>}'
                    content_len = int(self.headers.get('content-length'))
                    body = self.rfile.read(content_len)
                    data = json.loads(body)

                    # Check for 503
                    causal = data['causal-metadata']
                    if causal != None:
                        print("We have causal metadata")
                        socker = str(self.client_address[0]) + ":8090"
                        flag503 = False
                        if socker not in self.view:
                            print("CLIENT REQUEST CHECKING FOR CAUSAL METADATA")
                            indexOfOurSock = self.alwaysView.index(os.environ.get('SOCKET_ADDRESS'))
                            print("Causal: ", causal)
                            print("OurMetadata: ", self.metadata)
                            print("index of our sock: ", indexOfOurSock)
                            if len(self.metadata) < len(causal):
                                self.metadata.append(0)
                            elif len(self.metadata) > len(causal):
                                causal.append(0)
                            for i in range(0, len(self.metadata)):
                                if self.metadata[i] != causal[i]:
                                    flag503 = True
                        else:
                            print("Replica request checking for causal metadata")
                            indexOfClientSock = self.alwaysView.index(socker)
                            print("Causal: ", causal)
                            print("OurMetadata: ", self.metadata)
                            print("index of our sock: ", indexOfClientSock)
                            if len(self.metadata) < len(causal):
                                self.metadata.append(0)
                            elif len(self.metadata) > len(causal):
                                causal.append(0)
                            for i in range(0, len(self.metadata)):
                                if self.metadata[i] != causal[i]:
                                    flag503 = True

                        if flag503:
                            self.send_response(503)
                            self.send_header("Content-type", "application/json")
                            self.end_headers()
                            jsndict = {"error": "Causal dependencies not satisfied; try again later"}
                            jsnrtrn = json.dumps(jsndict)
                            self.wfile.write(jsnrtrn.encode("utf8"))
                            return

                    del self.keyValueStore[parsed_path[2]]

                    # update local causal metadata
                    if 'replica' not in data:
                        self.broadCastKVS(parsed_path[2], None, False)
                        index = self.alwaysView.index(os.environ.get('SOCKET_ADDRESS'))
                        self.metadata[index] = self.metadata[index] + 1
                        print("Delete Metadata ", self.metadata)
                    else:
                        index = self.alwaysView.index(data['sock'])
                        self.metadata[index] = self.metadata[index] + 1
                        print("Delete Metadata ", self.metadata)

                    # send back response
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = {"result": "deleted"}
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))
                #404 key dosent exist
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
