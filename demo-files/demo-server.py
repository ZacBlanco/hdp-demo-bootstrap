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
from gevent import monkey
monkey.patch_all()

log = logs.Logger('DEMO-SERVER.py').getLogger()

OUTPUTS = ['FILE', 'KAFKA', 'HTTP']

conf = config.read_config('global.conf')

app = Flask(__name__, static_url_path='')
app_port = int(conf['DEMO']['server_port'])
schema = conf['DEMO']['data_schema']
throughput = conf['DEMO']['bytes_per_second']
log_level = conf['LOGGING']['log-level']

# The Websockets will always be the demo_server port + 1
ws_port = app_port + 1

ws_app = cluster.WSDemoServer(ws_port)

dt = None

@app.route("/data-gen/start", methods=['POST'])
def start_data():
  '''Start the data generator
  
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
      data = {"message": str(e)}
      
      log.info('Returning JSON: ' + json.dumps(data))
  return flask.jsonify(**data)
  
@app.route("/data-gen/stop", methods=['POST'])
def stop_data():
  '''Stop the threaded data generator
  
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


@app.route("/data-gen/update", methods=['POST'])
def update_data():
  '''Update the data generator schema that will be used for the threaded generator and the temp generator for sample data
  
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
    GET'''
  global schema
  log.debug(json.dumps(schema))
  data = {
    'schema': schema,
    'message': 'successful retrieved schema'
  }
  return flask.jsonify(**data)


@app.route("/websockets/data", methods=['POST'])
def push_websockets():
  update_schema = request.get_json()
  update_schema = json.dumps(update_schema)
  ws_app.broadcast(update_schema)
  return ''


@app.route("/")
def index():
  '''Return the index to the UI'''
  return app.send_static_file('index.html')

if __name__ == "__main__":
  # Set up the Root Logger
  rootLogger = logging.getLogger()
  rootLogger.setLevel(logging.DEBUG)
  
  # Set up the PID file.
  try:
    os.remove(filedir + '/demo.pid')
  except OSError:
    pass
  pid = os.getpid()
  with open(filedir + '/demo.pid', 'w') as tf:
    tf.write(str(pid))

  # Start the Websocket Server
  ws_app.start()
  
  
#  Run!
#  app.debug=1
  app.run(host='0.0.0.0', port=app_port)
