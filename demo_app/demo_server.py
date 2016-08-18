'''This is the "main" file for the demo application. It houses the server and defines some API routes

This server is mainly built using flask. Config values are drawn from ``global.conf``

To run the server use the following command::

    python demo_server.py


'''
# First thing to do...
# Import the demo_utils module :)
import sys, os
filedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(filedir + '/../demo_utils')

import threading, time, json, flask, cluster, logging
from flask import Flask, request
from demo_utils import config, generator
from cluster import ThreadedGenerator
from demo_utils import logs
from ws4py import configure_logger
from flask_cors import CORS
log = logs.Logger('DEMO_SERVER.py').getLogger()

OUTPUTS = ['FILE', 'KAFKA', 'HTTP', 'HDFS']
'''The three different types of outputs from the generator'''

conf = config.read_config('global.conf')

app = Flask(__name__, static_url_path='')
CORS(app)
app_port = int(conf['DEMO']['server_port'])
schema = conf['DEMO']['data_schema']
throughput = conf['DEMO']['bytes_per_second']
log_level = conf['LOGGING']['log-level']

# The Websockets will always be the demo_server port + 1
ws_port = app_port + 1
'''The port for the websocket server'''

ws_app = cluster.WSDemoServer('0.0.0.0', ws_port)
'''The websocket server object. Used to broadcast messages'''

dt = None
'''The object to hold the ThreadedDataGenerator'''

@app.route("/data-gen/start", methods=['POST'])
def start_data():
  '''Start the data generator
  
  Route:
    ``POST /data-gen/start``
  
  Returns:
    json: A piece of JSON with a key "message" where the user can read the message back from the server'''
  data = {"message": "Started data generator"}
  outs = []
  for opt in OUTPUTS:
    if opt in request.form:
      outs.append(opt)
      
  log.info('Data generator outputs: ' + str(outs))
  if len(outs) <= 0:
    data = {"message": "Please select at least one output"}
    log.error('No generator outputs were selected')
    log.error('Data generator not started')
  else:    
    try:
      global dt
      if dt is None:
        dt = ThreadedGenerator(schema, int(throughput), outs)
        log.info('Starting threaded data generator')
        dt.start()
      else:
        data = {'message': "Data generator is already running"}
    except Exception as e:
      log.info('Error when starting threaded data generator. ')
      log.error(str(e))
      dt = None
      data = {"message": 'Error When starting threaded data generator. '+ str(e)}
      
      log.info('Returning JSON: ' + json.dumps(data))
  return flask.jsonify(**data)
  
@app.route("/data-gen/stop", methods=['POST'])
def stop_data():
  '''Stop the threaded data generator
  
  Route:
    ``POST /data-gen/stop``
  
  Returns:
    json: A JSON message determining whether or not the generator was stopped'''
  
  data = { 'message': '' }
  global dt
  log.info('Stopping data generator')
  if dt != None:
    dt.stop()
    dt = None
    data['message'] = 'Data generator stopped'
    log.info('Data generator stopped')
  else:
    data['message'] = 'Data generator was not running'
    log.info('Data generator was not running')
  return flask.jsonify(**data)

@app.route('/data-gen/queries', methods=['GET'])
def get_test_queries():
  dat = cluster.generate_queries(schema)
  return flask.jsonify(**dat)
  


@app.route("/data-gen/update", methods=['POST'])
def update_data():
  '''Update the data generator schema that will be used for the threaded generator and the temp generator for sample data
  
  Route:
    ``POST /data-gen/update``
  
  Returns:
    json: A JSON object with a 'message' key.
  '''
  
  update_schema = request.get_json()
  update_schema = json.dumps(update_schema)
  try:
    log.info('Updating schema for generator')
    g = generator.DataGenerator(update_schema)
    g.generate()
    data = {'message': 'Schema updated successfully'}
    log.info('schema updated successfully')
    global schema
    schema = update_schema
  except Exception as e:
    log.error('Unable to update the generator schema')
    data = {'message': str(e)}
  return flask.jsonify(**data)
  
@app.route("/data-gen/sample", methods=['GET'])
def get_sample():
  '''Get a sample piece of data from the data generator.
  
  Methods:
    GET
  
  Route:
    ``/data-gen/sample``
  
  Returns:
    json: The JSON data from the generator.
  '''
  try:
    g = generator.DataGenerator(schema)
    log.info('Generated data sample')
    return flask.jsonify(**g.generate())
  except:
    data = {'message': "Looks like we hit an exception somewhere..."}
    log.error('Unable to create sample data')
    return flask.jsonify(**data)

@app.route("/data-gen/schema", methods=['GET'])
def get_schema():
  '''Get the schema the generator is currently using
  
  Methods:
    GET
    
  Route:
    ``GET /data-gen/schema``
  
  Returns:
    json: The JSON object which represent the generator's schema
  
  
  '''
  global schema
  data = {
    'schema': schema,
    'message': 'successful retrieved schema'
  }
  return flask.jsonify(**data)


@app.route("/websockets/data", methods=['POST'])
def push_websockets():
  '''Broadcast a message to all Websocket clients
  
  Route:
    ``POST /websockets/data``
    
  Returns:
    N/A
  
  '''
  msg = request.get_json()
  msg = json.dumps(msg)
  ws_app.broadcast(msg)
  return ''


@app.route("/")
def index():
  '''Return the index to the UI
  
  Returns:
    html: The HTML for the app'''
  return app.send_static_file('index.html')

if __name__ == "__main__":
  # Set up the Root Logger
  rootLogger = logging.getLogger()
  rootLogger.setLevel(logging.DEBUG)
  log.info('Starting the demo application')
  configure_logger(True, './ws4py.log', logging.DEBUG);
  
  # Start the Websocket Server
  ws_app.start()
  
#  Run!
#  app.debug=1
  app.run(host='0.0.0.0', port=app_port)
