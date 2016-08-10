'''Run Shell commands through python

Usage:
  .. code-block:: python
    :linenos:
    
    from demo_utils.shell import Shell
    
    sh = Shell()
    
    sh.run('ls')
    sh.set_cwd('~')
    sh.set_cwd('/')
    sh.run('ls')
'''
import os, subprocess
from logs import Logger

logger = Logger('Shell').getLogger()

# The shell class defines just a few functions which can make executing commands easier
# run
#   This command has two possible ways to be called
#   (command) which is just a single line with all arguments
#   (command, args) which simply just joins a string with the command and arguments
#
# It is also possible to change the current working directory (cwd)
# for commands which are sensitive to file locations
# (Unfortunately 'cd' doesn't work)

# If no arguments are passed for args, then it is assumed to be a string of length 0
# If no arguments are passed to the constructor we assume default cwd

class Shell:

  def run(self, command, args=''):
    '''Run shell commands
    
    Args:
      command (str): command to run. You can add arguments afterwards
      args (list, optional): a list of string arguments which will be joined by spaces. Below is the implementation:
    
    .. code-block:: python
      
      if len(args) > 0:
        command = ' '.join([command, args.join(' ')])
          
    Returns:
      list: The output from ``subprocess.Popen``. This is a 2 element list of strings
      
        - [0] - stdout
        - [1] - stderr
     '''
    if len(args) > 0:
      command = ' '.join([command, args.join(' ')])
    
    path = os.getcwd()
    if len(self.cwd) > 0:
      logger.debug('Working Directory: ' + self.cwd)
      logger.info('Running Command: ' + command)
      process = subprocess.Popen(command, shell=True, cwd=self.cwd, stdout=subprocess.PIPE, stdin=subprocess.PIPE)
    else:
      process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
    output = process.communicate()
    return output


  # set_cwd
  # equivalent to doing a 'cd' command at the command line
  # Error if the directory doesn't exist
  def set_cwd(self, new_cwd):
    '''Set the current Working directory for the shell.
    
    ``cd`` doesn't work because we don't persist the subprocess between calls.
    
    When setting the working directory we are simply setting the ``cwd`` argument in ``subprocess.Popen``.
    
    Returns:
      N/A
      
    Raises:
      IOError: Raised when the directory we try to set doesn't exist.
    
    '''
    if new_cwd == '':
      self.cwd = ''
    elif not os.path.exists(new_cwd):
      logger.error('Directory ' + new_cwd + ' does not exist')
      raise IOError(' '.join([new_cwd, 'does not exist']))
    else:
      self.cwd = new_cwd

  def __init__(self, wd=''):
    self.set_cwd(wd)
    