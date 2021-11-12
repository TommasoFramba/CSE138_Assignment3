### Team Contributions:

Tommaso Framba :
* All view operations
* Server setup constructing and broadcast put view on server startup

Eric Yao Huang:

### Acknowledgements: 


### Citations:
Python HTTP Server Documentation https://docs.python.org/3/library/http.server.html This citation was used in order to reference what parts of the httpserver library was needed in order to implement proper handling of responses to GET and PUT and DELETE requests.

Python Requests Documentation https://docs.python-requests.org/en/latest/ This is the documentation on how to use the Python Requests library, which was used to implement request forwarding in part 2.

Python Sockets Documentation https://realpython.com/python-sockets/ This is the documentation on Python sockets that helped to implement detecting if the main server is down for part 2.

### Mechanism Description:
TODO: When a replica does Key-value operations it checks if the server is down and if it is then it broadcasts a delete view request to all other addresses in view.
