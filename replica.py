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
import socket


# handle requests
class helloHandler(BaseHTTPRequestHandler):
    keyValueStore = dict()

    # handle get requests
    def do_GET(self):
        parsed_path = urlparse(self.path).path.split("/")
        if len(parsed_path) == 2 and parsed_path[1] == 'kvs': parsed_path.append("")  # Handle as if it was empty string
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':

                # If key exists #200 OK else #404 Not Found
                if parsed_path[2] in self.keyValueStore:
                    self.send_response(200)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = {"result": "found", "value": self.keyValueStore[parsed_path[2]]}
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "application/json")
                    self.end_headers()
                    jsndict = {"error": "Key does not exist"}
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))

    # handle post requests
    def do_PUT(self):
        parsed_path = urlparse(self.path).path.split("/")
        if len(parsed_path) == 2 and parsed_path[1] == 'kvs': parsed_path.append("")  # Handle as if it was empty string
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':

                # Get Json body {"value": <value>}
                content_len = int(self.headers.get('content-length'))
                body = self.rfile.read(content_len)
                data = json.loads(body)

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

    def do_DELETE(self):
        parsed_path = urlparse(self.path).path.split("/")
        if len(parsed_path) == 2 and parsed_path[1] == 'kvs': parsed_path.append("")  # Handle as if it was empty string
        if len(parsed_path) == 3:
            if parsed_path[1] == 'kvs':
                if parsed_path[2] in self.keyValueStore:
                    del self.keyValueStore[parsed_path[2]]
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
                    jsndict = {"error": "Key does not exist"}
                    jsnrtrn = json.dumps(jsndict)
                    self.wfile.write(jsnrtrn.encode("utf8"))


# start and run server on port 8090
def main():
    if os.environ.get('FORWARDING_ADDRESS') == None:
        PORT = 8090
        server = HTTPServer(('', PORT), helloHandler)

        print('Server running on port %s' % PORT)

        server.serve_forever()


if __name__ == '__main__':
    main()