import os

print('WORKING DIRECTORY: ' + os.getcwd())
print('FILE DIRECTORY: ' + os.path.abspath(__file__))
print('OS DIR: ' + os.path.dirname(os.path.abspath(__file__)))
