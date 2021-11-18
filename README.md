### Team Contributions:

Tommaso Framba :
* All view operations
* Basic KVS operations
* Server setup constructing and broadcast put view on server startup
* Vector clocks implementation
* Causal consistency implementation
* Put and delete broadcasts
* Down detection for put and delete kvs broadcasts

Eric Yao Huang:
* Basic KVS operations
* Vector clocks implementation 
* Vector clocks functions/manipulation
* Functions to check causal consistency
* Cleaned up and refactored code for submission


### Acknowledgements: 
Tommaso would like to acknowledge TA Patrick for responding to Yuja posts for other students issues that related to my own and several of my own issues. These issues specifficaly related to testing when a replica disconnects from the network and partitions itself versus killing itself. 

Eric would like to acknowledge TA Patrick Redmond for providing pseudocode and general guidance during the sections.

### Citations:
Python HTTP Server Documentation https://docs.python.org/3/library/http.server.html This citation was used in order to reference what parts of the httpserver library was needed in order to implement proper handling of responses to GET and PUT and DELETE requests.

Python Requests Documentation https://docs.python-requests.org/en/latest/ This is the documentation on how to use the Python Requests library, which was used to implement request forwarding in broadcast messaging instances.

Python Sockets Documentation https://realpython.com/python-sockets/ This is the documentation on Python sockets that helped to implement detecting if the main server is down for down detection in broadcasting instances of PUT and DELETE.

### Mechanism Description:
Our system tracks causal dependencies through the use of an array of numbers as a vector clock. Each replica in the view is mapped to an index on the vector clock, and initialized at startup. When a replica requests to join the group, it receives a copy of the vector clock from replica. The vector clock of the sender and receiver is compared every time a replica receives a request, and it is incremented every time a PUT or DELETE is requested by a client. 

We detect if a replica is down using the following methodology. When a replica does a PUT or DELETE it opens a socket to all addresses in view and pings them with a five second timeout. If the timeout occurs and there is no response it is appended to a list of views to delete. It then calls the deleteViews method that deletes non responsive views on the replica that got the request and forwards a delete view to all other replicas that are still alive.  
