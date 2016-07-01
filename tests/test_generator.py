import unittest, json, mock, random
from env import scripts
from mock import Mock
from scripts.generator import DataGenerator
from scripts.generator import AbstractDatum

class TestDataGenerator(unittest.TestCase):
	
	@mock.patch('scripts.config.get_conf_dir', return_value='res/')
	def test_string_datum_good(self, mock1):
		gen = DataGenerator('char_gen_good.json', seed='1234567890')
		test_num = 500
		data = []
		for i in range(test_num):
			data.append(gen.generate())
		
		occ = {}
		total = 0
		for items in data:
			for char in items:
				total += 1
				if char in occ:
					occ[char] += 1
				else:
					occ[char] = 1
						
#		for key in occ.keys():
#			print("KEY: " + key + " | OCC: " + str(occ[key]) + " | PROB: " + str( occ[key]/float(test_num) ))
		
		assert total == 4*test_num
		assert occ['a'] == 138
		assert occ['c'] == 111
		assert occ['b'] == 127
		assert occ['e'] == 132
		assert occ['d'] == 124
		assert occ['g'] == 112
		assert occ['f'] == 145
		assert occ['i'] == 260
		assert occ['h'] == 111
		assert occ['k'] == 102
		assert occ['j'] == 90
		assert occ['m'] == 93
		assert occ['l'] == 48
		assert occ['o'] == 23
		assert occ['n'] == 362
		assert occ['p'] == 22

	@mock.patch('scripts.config.get_conf_dir', return_value='res/')
	def test_gen_key_check_field(self, mock1):
		try:
			gen = DataGenerator('char_gen_bad-01.json', seed='1234567890')
			self.fail('Should have failed with KeyError on fieldName')
		except KeyError as e:
			assert("Could not find 'fieldName' in field of schema:" in str(e))
			
	@mock.patch('scripts.config.get_conf_dir', return_value='res/')
	def test_gen_key_check_type(self, mock1):
		try:
			gen = DataGenerator('char_gen_bad-02.json', seed='1234567890')
			self.fail('Should have failed with KeyError on type')
		except KeyError as e:
			assert('Could not find \'type\' in field of schema:' in str(e))
			
	@mock.patch('scripts.config.get_conf_dir', return_value='res/')
	def test_gen_key_check_root(self, mock1):
		try:
			gen = DataGenerator('char_gen_bad-03.json', seed='1234567890')
			self.fail('Should have failed with TypeError')
		except TypeError as e:
			assert('Root of JSON Schema is not a list' in str(e))

		
	@mock.patch('scripts.config.get_conf_dir', return_value='res/')
	def test_gen_check_field_type(self, mock1):
		try:
			gen = DataGenerator('char_gen_bad-04.json', seed='1234567890')
			self.fail('Should have failed with TypeError')
		except RuntimeError as e:
			assert('Field type was not found. Please change the field type or implement a new datum' in str(e))
			
	@mock.patch('scripts.config.get_conf_dir', return_value='res/')
	def test_gen_check_values(self, mock1):
		try:
			gen = DataGenerator('char_gen_bad-05.json', seed='1234567890')
			self.fail('Should have failed with KeyError')
		except KeyError as e:
			assert('Missing key: values in field3' in str(e))

	@mock.patch('scripts.config.get_conf_dir', return_value='res/')
	def test_gen_abstract_datum(self, mock1):
		try:
			field = {}
			field['fieldName'] = "ABC123"
			field['type'] = "ABC123"
			dat = AbstractDatum(field)
			dat.check()
			self.fail('Should raise not implemented error')
		except NotImplementedError as e:
			assert('AbstractDatum: This method should have been implemented by a sublcass' in str(e))
			
		try:
			field = {}
			field['fieldName'] = "ABC123"
			field['type'] = "ABC123"
			dat = AbstractDatum(field)
			dat.generate(random)
			self.fail('Should raise not implemented error')
		except NotImplementedError as e:
			assert('AbstractDatum: This method should have been implemented by a sublcass' in str(e))

		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		
		