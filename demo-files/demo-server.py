# First thing to do...
# Import the demo_utils module :)
import sys, os
filedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(filedir + '/../demo_utils')


import threading, time, json, flask
from flask import Flask, request
from demo_utils import config, generator

conf = config.read_config('global.conf')
app = Flask(__name__, static_url_path='')
app_port = conf['DEMO']['port']
schema = conf['DEMO']['data_schema']
throughput = conf['DEMO']['bytes_per_second']
dt = None

@app.route("/data-gen/start", methods=['POST'])
def start_data():
  data = {"message": "Started data generator"}
  try:
    global dt
    if dt is None:
      dt = GenData(schema, int(throughput))
      dt.start()
    else:
      data = {'message': "Data generator is already running"}
  except Exception as e:
    data = {"message": str(e)}
  return flask.jsonify(**data)
  
@app.route("/data-gen/stop", methods=['POST'])
def stop_data():
  data = { 'message': ''}
  global dt
  if dt != None:
    dt.stop()
    dt = None
    data['message'] = 'Data generator stopped'
  else:
    data['message'] = 'Data generator was not running'
  return flask.jsonify(**data)


@app.route("/data-gen/update", methods=['POST'])
def update_data():
  update_schema = request.get_json()
  update_schema = json.dumps(update_schema)
  try:
    g = generator.DataGenerator(update_schema)
    g.generate()
    data = {'message': 'Schema updated successfully'}
    global schema
    schema = update_schema
  except Exception as e:
    print str(e)
    data = {'message': str(e)}
  return flask.jsonify(**data)
  
@app.route("/data-gen/sample", methods=['GET'])
def get_sample():
  g = generator.DataGenerator(schema)
  return flask.jsonify(**g.generate())

@app.route("/data-gen/schema", methods=['GET'])
def get_schema():
  global schema
  data = {
    'schema': schema,
    'message': 'successful retrieved schema'
  }
  return flask.jsonify(data)

@app.route("/")
def index():
  return app.send_static_file('index.html')

class GenData(threading.Thread):
  def __init__(self, schema, bps):
    threading.Thread.__init__(self)
    self.daemon = True
    self.flag = True
    if bps > 0:
      self.bps = bps
    else:
      self.bps = 50000 #50kb
    self.gen = generator.DataGenerator(schema)
  
  def run(self):
    while self.flag:
      bytes = 0
      lines = 0
      start = time.time()
      # generate all the data and do something with it
      while bytes <= self.bps:
        data = self.gen.generate()
        bits = len(json.dumps(data).encode('utf-8'))
        bytes = bytes + bits
        # Now export the data somewhere.....
      # sleep until the next second once we've generated enough data
      while (time.time() - start <= 1):
        time.sleep(0.1)

  def stop(self):
    self.flag = False
  

if __name__ == "__main__":
  try:
    os.remove(filedir + '/demo.pid')
  except OSError:
    pass
  pid = os.getpid()
  with open(filedir + '/demo.pid', 'w') as tf:
    tf.write(str(pid))
  app.run(host='0.0.0.0', port=app_port)
