[Back to Index](README.md)

# CurlClient

`curl_client.py` is a module that houses the `CurlClient` class. This class utilizes the `shell.py` module in order to build `curl` commands to make HTTP requests.

## Usage
	
Sample Usage:

	from curl_client import CurlClient
	client = CurlClient(username, password, protocol, server, port)
	
	client.make_request('GET', '/api/v1/clusters', '-k', '')


## Methods

### `CurlClient.__init__(username='', password='', proto='http', server='127.0.0.1', port=8080)`

Initializes the CurlClient object. 

Defaults:

| Parameter | Value | 
|-----------|-------|
| `proto`   |`http` |
| `server`  |`127.0.0.1`|
| `port`    | `8080`|

These parameters are used in all requests made by the CurlClient

### `CurlClient.make_request(verb, request, options='', query='')`

Returns a two item array of the command output. One element for `std_out` and another element for `std_err` which is propagated from the `shell.py` module. The first element in `std_out` where the second element is `std_err`

	[std_out, std_err]
	output[0] = std_out
	output[1] = std_err

##### Required parameters:

- verb
- request

`verb` is one of the four basic HTTP verbs. It must be one of: 

- GET
- PUT
- POST
- DELETE

`request` is the path to which you want to make your request.

Given a server with an API endpoint at `http://127.0.0.1:8080` with a a `request` parameter of `/request/path`

The curl call made might look something like

	curl -u username:password -X GET http://127.0.0.1:8080/request/path
	
The value of `request` is simply appended to the address of the server.

##### Optional Parameters

- options
- query

`options` allows you to add more command line options to the curl request. You can add things like `-k` or `-i` if desired for the testing environment

`query` allows you to add query parameters to the HTTP requests at the end of the url. 

Example:

- `query = fields=tasks/Tasks`

	curl -u username:password -X GET http://127.0.0.1:8080/request/path?fields=tasks/Tasks


### `CurlClient.set_username(user)`

Updates the the desired username to make REST calls to web server. (May be left empty if not needed)

### `CurlClient.set_password(password)`

Updates the the desired password to make REST calls to web server. (May be left empty if not needed)

**NOTE:** This should _not_ be used in a secure environment. Sensitive passwords should not be used nor stored here. This framework is designed for **test environments only**

### `CurlClient.set_proto(proto)`

Updates the the desired protocol to make REST calls to the web service. The only values allowed are '`http`' and '`https`'

### `CurlClient.set_server(server)`

Updates the the desired server hostname/IP Address of the location of web server.

### `CurlClient.set_port(port)`

Updates the desired port on which web server is running. **Must be an integer**.




