# Script which installs Zeppelin as an Ambari Service
import config, sys, platform, json, time, os
from shell import Shell
from curl_client import CurlClient
from logs import Logger

logger = Logger('service_installer').getLogger()

def install_hdp_select():
  '''Installs the hdp-select package.
  
  This is used to help install the Ambari Service for NiFi/Zeppelin. Retrieves the currently installed hadoop version.
  
  Typically the Sandbox has hdp-select already, but clusters won't always have it, which is why we provide this method.
  
  
  '''
  logger.info('Determining whether system is compatible with hdp-select')
  dist_info = platform.linux_distribution()
  if(len(dist_info[0]) == 0):
    logger.critical('Non Linux System. Could not install hdp-select')
    raise EnvironmentError('You must be running a linux distribution to install hdp-select')
    
#  Only want to get distro name
#  Determine first distro name
#    Then determine the version (first char char for centos )
  distro = dist_info[0].lower()
  fullname = distro
  ver = dist_info[1]
  if 'centos' in distro: # Get First 1/2 nums in version string
    fullname = fullname + dist_info[1][0]
    logger.info('Determined we are running CentOS')
  elif 'ubuntu' in distro:
    logger.info('determined we are running ubuntu')
    if (len(dist_info[1]) < 2):
      fullname = fullname + dist_info[1][0]
    else:
      fullname = fullname + dist_info[1][0] + dist_info[1][1]
  
  conf = config.read_config('global.conf')
  urls = conf['HDP-SELECT']
  url = ''
  if fullname == 'centos6':  
    url = urls['centos6']
  elif fullname == 'centos7':
    url = urls['centos7']
  elif fullname == 'ubuntu12':
    url = urls['ubuntu12']
  elif fullname == 'ubuntu14':
    url = urls['ubuntu14']
  
  res = ''
  
  logger.info('Checking if hdp-select is installed')
  if len(url) == 0:
    logger.error('Not using CentOS6/7 or Ubuntu12.x/14.x')
    raise EnvironmentError('Must be using one of: CentOS 6.x, CentOS 7.x, Ubuntu 12.x, Ubuntu 14.x')
  elif 'centos' in fullname:
    cmd = Shell()
    output = cmd.run('yum install -y ' + url)
    res = cmd.run('which hdp-select')
  elif 'ubuntu' in fullname:
    cmd = Shell()
    output = cmd.run('wget ' + url + ' -O ./hdp-select.deb')
    output = cmd.run('dpkg -i ' + './hdp-select.deb')
    res = cmd.run('which hdp-select')
    
  if len(res[0]) == 0:
    logger.info('hdp-select did not install successfully')
    return False
  else:
    logger.info('hdp-select installed successfully')
    return True
  
def is_hdp_select_installed():
  '''Checks if ``hdp-select`` is installed.
  
  Returns:
    bool: True if installed (available as shell command), False if not installed'''
  sh = Shell()
  output = sh.run('which hdp-select')
  
  if len(output[0]) == 0:
    return False
  else:
    return True

def is_ambari_installed():
  '''Determines whether or not ``ambari-server`` is available (In order to start/stop/restart Ambari)
  
  Returns:
    bool: True is ``ambari-server`` is available as a shell command. False otherwise.
  
  '''
  sh = Shell()
  output = sh.run('which ambari-server')
  if len(output[0]) == 0:
    return False
  else:
    return True
  
# Uses the conf/zeppelin/notes directory to upload pre-made notebooks
def add_zeppelin_notebooks():
  '''Add all Zeppelin notes to the current Zeppelin instalation
  
  Looks inside ``configuration/zeppelin/notes`` for any ``*.json`` files.
  
  Each JSON file will be attempted to be added to the current Zeppelin instance
  
  Returns:
    bool: True is every Note was added successfully. True is returned on an empty directory. False otherwise.
  
  
  '''
  logger.info('Adding zeppelin notebooks to installation')
  all_success = True
  note_dir = config.get_conf_dir() + 'zeppelin/notes'
  
  # First need to authenticate to Zeppelin and retrieve JSESSIONID
  conf = config.read_config('global.conf')['ZEPPELIN']
  session = get_zeppelin_session(conf['username'], conf['password'])
  
  for item in os.listdir(note_dir):
    logger.debug('Found item in zeppelin/notes: ' + item)
    item_path = note_dir + '/' + item
    if os.path.isfile(item_path) and str(item).endswith('.json'):
      logger.info('POSTing ' + item + ' to Zeppelin')
      result = post_notebook(item_path, session)
      if not result:
        logger.error('Not all notebooks were added to Zeppelin successfully')
        all_success = False
  return all_success

def get_zeppelin_session(username, password):
  '''Gets the JSESSIONID cookie by POSTing to /api/login
  
  This is required to retrieve the JSESSIONID on Zeppelin instances that have logins and user permissions. Used when POSTing notebooks as well.
  
  Returned in the form of ``'JSESSIONID=**``
  
  Args:
    username (str): The username to login with
    password (str): The password to login with
    
  Returns:
    str: ``''`` If the request was unsuccessful, or the cookie wasn't present. Otherwise returns the cookie as a string.
  '''
  conf = config.read_config('global.conf')['ZEPPELIN']
  client = CurlClient(proto=conf['protocol'], server=conf['server'], port=int(conf['port']))
  path = '/api/login'
  opts = '-i -d \'userName=' + username + '&password=' + password + '\''
  res = client.make_request('POST', path, options=opts)
  lines = res[0].split('\n')
  for line in lines:
    if 'Set-Cookie:'.lower() in line.lower() and 'JSESSIONID' in line.upper():
      cookie = line.split('Set-Cookie: ')[1]
      print 'COOKIE: ' + cookie
      return cookie.strip()
  return ''

def post_notebook(notebook_path, session_cookie=''):
  '''Add a single notebook to a Zeppelin installation via REST API
  
  Must have a file called ``global.conf`` inside of the configuration directory.
  
  Inside that configuration file we use protocol://server:port to connect to a Zeppelin instance and use the API
  
  Args:
    notebook_path (str): Full file path to the Zeppelin note
    session_cookie (str, optional): The cookie used after authentication in order to make authorized API calls. Required on the 2.5 TP Sandbox
    
  Returns:
    bool: True if the upload was successful (received 201 created), or False otherwise.
  
  '''
  conf = config.read_config('global.conf')['ZEPPELIN']
  client = CurlClient(proto=conf['protocol'], server=conf['server'], port=int(conf['port']))
  path = '/api/notebook'
  
  logger.info('Attempting to POST notebook at ' + client.proto + '://' + client.server + ':' + str(client.port))
  opts = '-i -b \'' + session_cookie + '\' -H "Content-Type: application/json" -d @' + notebook_path
  output = client.make_request('POST', path, options=opts)
  if '201 created' in output[0].lower():
    logger.info('Note posted successfully')
    return True
  else:
    logger.info('Note failed to be added. User will need to add manually')
    return False

def add_nifi_templates():
  '''Add any number of NiFi templates to a running NiFi installation via the REST API
  
  Looks inside ``configuration/nifi/templates`` for XML templates to add to the installation
  
  Returns:
    bool: True if we were successful in uploading every template. False otherwise. An empty directory results in True
  '''
  logger.info('Attempting to add NiFi templates')
  all_success = True
  template_dir = config.get_conf_dir() + 'nifi/templates'
  for item in os.listdir(template_dir):
    logger.debug('Found item in nifi/templates: ' + item)
    item_path = template_dir + '/' + item
    if os.path.isfile(item_path) and str(item).endswith('.xml'):
      result = post_template(item_path)
      if not result:
        logger.error('Not all templates were added to NiFi successfully')
        all_success = False
  return all_success


def post_template(template_path):
  '''Add a single template to a NiFi instance via REST API
  
  
  Args:
    template_path (str): The full path to the NiFi template
    
  Returns:
    bool: True if the upload is successful, False otherwise
  
  '''
  conf = config.read_config('global.conf')['NIFI']
  client = CurlClient(proto=conf['protocol'], server=conf['server'], port=int(conf['port']))
  path = '/nifi-api/controller/templates'
  logger.info('Attempting to POST notebook at ' + client.proto + '://' + client.server + ':' + str(client.port))
  output = client.make_request('POST', path, options='-i -F template=@' + template_path )
  if '201 Created' in output[0] or '200 OK' in output[0]:
    logger.info('Template added to NiFi successfully')
    return True
  else:
    logger.info('Template failed to POST to NiFi')
    return False

def install_zeppelin():
  '''Install Zeppelin via Ambari.
  
  This requires user interaction. Plans to make installation automatic are in the works...
  
  Returns:
    bool: True if installation is successful. Else, the user specifies whether or not they want to continue setting up the demo without Zeppelin. ``True`` if the user specifed Yes (to continue). ``False`` if they specified No (do not continue).
  
  Raises:
    EnvironmentError: Raised when Ambari is not installed on the current host. Or if ``hdp-select`` cannot be installed'''
  
  logger.info('Attempting to install Zeppelin to the cluster')
  if not is_ambari_installed():
    logger.critical('Ambari must be installed on the system to continue with installation of zeppelin')
    raise EnvironmentError('You must install the demo on the same node as the Ambari server. Install Ambari here or move to another node with Ambari installed before continuing')
  
  if not is_hdp_select_installed():
    installed = install_hdp_select()
    if not installed:
      logger.critical('hdp-select must be installed on the system to continue with the installation of Zeppelin')
      raise EnvironmentError('hdp-select could not be installed. Please install it manually and then re-run the setup.')
  
  conf = config.read_config('global.conf')
  cmds = conf['ZEPPELIN']['install-commands']
  cmds = json.loads(conf['ZEPPELIN']['install-commands'])
  
  
  sh = Shell()
  logger.info('Getting HDP Version')
  version = sh.run(cmds[0])
  logger.info('HDP Version: ' + version[0])
  fixed_cmd = cmds[1].replace('$VERSION', str(version[0])).replace('\n', '')
  logger.info('Copying Files with command: ' + fixed_cmd)
  copy = sh.run(fixed_cmd)
  logger.info('Restarting Ambari Server....')
  restart = sh.run(cmds[2])

  logger.info('Ambari server restarted')
  logger.info('Waiting for user to install service in Ambari to continue')
  print("Please open the Ambari Interface and manually deploy the Zeppelin Service.")
  raw_input("Press enter twice to continue...")
  raw_input("Press enter once to continue...")
  
#   We've copied the necessary files. Once that completes we need to add it to Ambari
  
  print('Checking to make sure service is installed')
  ambari = config.read_config('global.conf')['AMBARI']
  
  installed = check_ambari_service_installed('ZEPPELIN', ambari)
  logger.info('Zeppelin installed successfully: ' + str(installed))
  cont = ''
  if not installed:
    print('Unable to contact Ambari Server. Unsure whether or not Zeppelin was installed')
    while not (cont == 'y' or cont == 'n'):
      cont = raw_input('Continue attempt to set up Zeppelin for demo?(y/n)')
      if not (cont == 'y' or cont == 'n'):
        print('Please enter "y" or "n"')
  else:
    cont = 'y'
  
  if cont == 'n':
    return False
  elif cont == 'y':
    return True



def install_nifi():
  '''Install NiFi via Ambari. (And Ali's NiFi service)
  
  This requires user interaction. Plans to make installation automatic are in the works...
  
  Returns:
    bool: True if installation is successful. Else, the user specifies whether or not they want to continue setting up the demo without Zeppelin. ``True`` if the user specifed Yes (to continue). ``False`` if they specified No (do not continue).
  
  Raises:
    EnvironmentError: Raised when Ambari is not installed on the current host. Or if ``hdp-select`` cannot be installed'''
  logger.info('Attempting to install NiFi to the cluster')
  if not is_ambari_installed():
    logger.error('Ambari must be installed to install NiFi as well.')
    raise EnvironmentError('You must install the demo on the same node as the Ambari server. Install Ambari here or move to another node with Ambari installed before continuing')
  
  
  if not is_hdp_select_installed():
    installed = install_hdp_select()
    if not installed:
      logger.error('hdp-select must be installed to install NiFi')
      raise EnvironmentError('hdp-select could not be installed. Please install it manually and then re-run the setup.')

  conf = config.read_config('global.conf')
  cmds = json.loads(conf['NIFI']['install-commands'])
  
  sh = Shell()
  logger.info('Getting HDP Version')
  version = sh.run(cmds[0])
  logger.info('HDP Version: ' + version[0])
  fixed_copy = cmds[2].replace('$VERSION', str(version[0])).replace('\n', '')
  fixed_remove = cmds[1].replace('$VERSION', str(version[0])).replace('\n', '')
  logger.info('NiFi Clean Command: ' + fixed_copy)
  logger.info('NiFi Copy Command: ' + fixed_remove)
  remove = sh.run(fixed_remove)
  copy = sh.run(fixed_copy)
  logger.info('Attempting to restart Ambari...')
  restart = sh.run(cmds[3])

  print("Please open the Ambari Interface and manually deploy the NiFi Service.")
  raw_input("Press enter twice to continue...")
  raw_input("Press enter once to continue...")
  
#   We've copied the necessary files. Once that completes we need to add it to Ambari
  logger.info('Waiting for user to install service in Ambari to continue')
  print('Checking to make sure service is installed')
  ambari = config.read_config('global.conf')['AMBARI']
  installed = check_ambari_service_installed('NIFI', ambari)
  logger.info('NiFi installed successfully')
  cont = ''
  if not installed:
    print('Unable to contact Ambari Server. Unsure whether or not Zeppelin was installed')
    while not (cont == 'y' or cont == 'n'):
      cont = raw_input('Continue attempt to set up NiFi for demo?(y/n)')
      if not (cont == 'y' or cont == 'n'):
        print('Please enter "y" or "n"')
  else:
    cont = 'y'
  
  if cont == 'n':
    return False
  elif cont == 'y':
    return True


  
def check_ambari_service_installed(service_name, ambari_config):
  '''Determine whether an Ambari service is installed.
  
  Args:
    service_name (string): Name of service to look for
    ambari_config (dict): The entire AMBARI section of ``global.conf``
      ::
      
        read_config('global.conf')['AMBARI']
        
  Returns:
    bool: True service exists, False if the service does not exist
    '''
  curl = CurlClient(username=ambari_config['username'], password=ambari_config['password'], port=ambari_config['port'], server=ambari_config['server'], proto=ambari_config['proto'])
  logger.info('Checking if Ambari service: ' + service_name + ' is installed')
  cluster_name = ambari_config['cluster_name']
  request = '/api/v1/clusters/' + cluster_name + '/services/' + service_name
  attempts = 0
  while attempts < 10:
    output = curl.make_request('GET', request, '-i')
    if '200 OK' in output[0]:
      print('Service Installed Sucessfully')
      logger.info(service_name + ' was installed successfully')
      return True
    else:
      attempts += 1
      raw_input('Could not connect.' + str(10-attempts) + ' remaining. Press any key to continue')
  
  logger.info(service_name + ' was not installed successfully')
  return False












  
  
  