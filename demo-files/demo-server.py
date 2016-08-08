# First thing to do...
# Import the demo_utils module :)
import os, sys
filedir = os.path.dirname(os.path.realpath(__file__))
sys.path.append(filedir + '/../demo_utils')
from flask import Flask
from demo_utils import config, ambari

conf = config.read_xml_config('demo-config.xml')
app = Flask(__name__, static_url_path='')
app_port = conf['demo.server.port']


@app.route("/data-gen/start", methods=['POST'])
def start_data():
  return "started"
  
@app.route("/data-gen/stop", methods=['POST'])
def stop_data():
  return "stopped"
  
@app.route("/data-gen/update", methods=['POST'])
def update_data():
  return "updated"
  
@app.route("/data-gen/sample", methods=['GET'])
def get_sample():
  return "sampled"

@app.route("/")
def index():
  return app.send_static_file('index.html')


if __name__ == "__main__":
  try:
    os.remove(filedir + '/demo.pid')
  except OSError:
    pass
  pid = os.getpid()
  with open(filedir + '/demo.pid', 'w') as tf:
    tf.write(str(pid))
  app.run(host='0.0.0.0', port=app_port)
