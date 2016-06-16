import unittest
from env import scripts
from scripts.shell import Shell

class TestShell(unittest.TestCase):
	def test_default_cwd(self):
		try:
			cmd = Shell()
		except IOError as e:
			self.fail('No argument shell constructor should not raise IOError')

	def test_nonexistent_cwd(self):
		try:
			cmd = Shell('/missing/directory')
			self.fail('Should raise IOError on setting nonexistent directory')
		except IOError as e:
			return

	def test_existing_directory(self):
		try:
			# Actual Directory
			cmd = Shell('/tmp')
		except IOError as e:
			self.fail('Valid path should pass here')

	def test_simple_run(self):
		cmd = Shell();
#		out = cmd.run('bash --version')
#		out = cmd.run('bash', '--version')
		out = cmd.run('bash')
		print('')
		print(out)