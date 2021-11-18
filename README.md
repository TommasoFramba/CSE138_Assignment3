### Team Contributions:

Tommaso Framba :
* All view operations
* Server setup constructing and broadcast put view on server startup
* Down detection for put and delete kvs broadcasts
* All kvs operations

Eric Yao Huang:
* Vector clocks implementation and 503 causal consistency implementation to all kvs methods
* Cleaned up code for submittal
* Put and delete broadcasts

### Acknowledgements: 
Tommaso would like to acknowledge TA Patrick for responding to Yuja posts for other students issues that related to my own and several of my own issues. These issues specifficaly related to testing when a replica disconnects from the network and partitions itself versus killing itself. 

### Citations:
Python HTTP Server Documentation https://docs.python.org/3/library/http.server.html This citation was used in order to reference what parts of the httpserver library was needed in order to implement proper handling of responses to GET and PUT and DELETE requests.

Python Requests Documentation https://docs.python-requests.org/en/latest/ This is the documentation on how to use the Python Requests library, which was used to implement request forwarding in part 2.

Python Sockets Documentation https://realpython.com/python-sockets/ This is the documentation on Python sockets that helped to implement detecting if the main server is down for part 2.

### Mechanism Description:
When a replica does a PUT or DELETE it opens a socket to all addresses in view and pings them with a five second timeout. If the timeout occurs and there is no response it is appended to a list of views to delete. It then calls the deleteViews method that deletes non responsive views on the replica that got the request and forwards a delete view to all other replicas that are still alive.  
