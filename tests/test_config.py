from env import scripts
from scripts import config
from ConfigParser import MissingSectionHeaderError

def test_good_file():
	params = config.read_config('res/good-test.properties')
	assert params['SECTION1']['key1'] == 'val1'
	assert params['SECTION2']['key2'] == 'val2'
	assert params['SECTION3']['key3'] == 'val3'
	assert params['SECTION3']['key4'] == 'val4'
	assert len(params['SECTION3']) > 1
	assert len(params['SECTION2']) > 0
	assert len(params['SECTION1']) > 0
	assert len(params) == 3
	
def test_missing_header():
	try:
		params = config.read_config('res/bad-test.properties')
		assert 0
	except MissingSectionHeaderError as err:
		assert 1
		
def test_missing_file():
	try:
		params = config.read_config('nofile')
		assert 0
	except IOError as e:
		if 'could not find file' not in e.message:
			assert 0