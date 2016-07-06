[Back to Index](README.md)

# Ambari

`ambari.py` is a module that houses the `Ambari` class. This class can make remote calls to an instance of the Ambari REST API.

This module utilizes [`curl_client.py`](curl_client.md) in order to make the RESTful API calls to an Ambari instance.

In its current state there is not much functionality, but more calls can be made possible by using the underlying [`curl_client`](curl_client.md) module to make REST calls to the API if the current features are not enough

--------

## Methods

### `Ambari.__init__(username='', password='', proto='http', server='127.0.0.1', port=8080)`

The Ambari client can take anywhere between 0 and 5 different arguments:

- username - (username to login to Ambari)
- password - (password to login to Ambari)
- proto - (The protocol used by Ambari Server. Must be one of: 'http' or 'https')
- server - (The IP address or hostname of the Ambari server)
- port - (The port on which ambari server is running)

The defaults for each of the above are shown in the argument list.

### `Ambari.service_action(cluster_name, service_name, action)`

- `action`
  - Must only be one one of: `'START'`, `'STOP'`, or `'RESTART'`

Makes RESTful API call to `GET /api/v1/clusters/{cluster_name}/{service_name}` in order to Stop/Start/Restart a given service.

Returns `True` or `False` based on whether or not the action was successful

This function utilizes `self.service_wait_time` to determine the longest amount of time we wait before failing the process

This function will return `True` or `False` based on whether or not the service was successful in starting, stopping, or restarting

### `Ambari.get_service(cluster_name, service_name, query='')`

Makes RESTful API call to `GET /api/v1/clusters/{cluster_name}/{service_name}`

Returns a piece of JSON via `json.loads` from the API.

If an error occurred when making the call to Ambari the error message from the curl client will be returned in the following format:

	{
		"message": error_message_string
	}

### `Ambari.get_clusters(query='')`

Makes RESTful API call to `GET /api/v1/clusters`

Returns a piece of JSON via `json.loads` from the API.

If an error occurred when making the call to Ambari the error message from the curl client will be returned in the following format:

	{
		"message": error_message_string
	}

### `Ambari.get_services(cluster_name, query='')`


Makes RESTful API call to `GET /api/v1/clusters/{CLUSTER_NAME}/services`

Returns a piece of JSON via `json.loads` from the API.

If an error occurred when making the call to Ambari the error message from the curl client will be returned in the following format:

	{
		"message": error_message_string
	}


### `Ambari.get_cluster_info(cluster_name, query='')`

Makes RESTful API call to `GET /api/v1/clusters/{CLUSTER_NAME}`

Returns a piece of JSON via `json.loads` from the API.

If an error occurred when making the call to Ambari the error message from the curl client will be returned in the following format:

	{
		"message": error_message_string
	}
	
### `Ambari.set_username(user)`

Updates the the desired username to make REST calls to Ambari

### `Ambari.set_password(password)`

Updates the the desired password to make REST calls to Ambari

**NOTE:** This should _not_ be used in a secure environment. Sensitive passwords should not be used nor stored here. This framework is designed for **test environments only**

### `Ambari.set_proto(proto)`

Updates the the desired protocol to make REST calls to Ambari. The only values allowed are '`http`' and '`https`'

### `Ambari.set_server(server)`

Updates the the desired ambari server hostname/IP Address to make REST calls to Ambari.

### `Ambari.set_port(port)`

Updates the desired port on which Ambari is running. **Must be an integer between 0 and 65535**.

### `Ambari.set_service_wait_time(wait_time)`

Updates the total amount of **time in seconds** that we will wait before assuming a service has failed to Stop/Start. **Must be a number greater than 0**.




