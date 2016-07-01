import json, config, random
from abc import abstractmethod


class DataGenerator():
	
	def __init__(self, schema, seed=''):
		self.data_fields = []
		self.schema = schema
		if not seed == '':
			random.seed(seed)
		self.check_schema(schema)
				
	# Returns true/false whether or not the schema is valid
	# Raises an exception?
	def check_schema(self, schema):
		path = config.get_conf_dir() + schema

		with open(path) as data_file:
			conf = json.load(data_file)
			
			if not type(conf) == list:
				raise TypeError('Root of JSON Schema is not a list')
			
			for field in conf:
				if not 'fieldName' in field:
					raise KeyError('Could not find \'fieldName\' in field of schema: ' + schema )
					
				if not 'type' in field:
					raise KeyError('Could not find \'type\' in field of schema: ' + schema)
				
				
				field_type = field['type']
				datum = AbstractDatum(field)
				if 'string' == field_type:
					datum = StringDatum(field)
				else:
					raise RuntimeError('Field type was not found. Please change the field type or implement a new datum')
					
				datum.check() # Check to make sure the field has necessary attributes	
#				print("FIELD LENGTH: " + str(len(self.data_fields)))
				self.data_fields.append(datum)
		
	def generate(self):
		data = []
		for field in self.data_fields:
			val = field.generate(random)
			data.append(val)
		return data


class AbstractDatum(object):
		
	def __init__(self, field):
		self.field_name = field['fieldName']
		self.field = field
		self.check_for_key('fieldName')
	
	def check_for_key(self, key_name):
		if not key_name in self.field:
			raise KeyError('Missing key: ' + key_name + ' in ' + self.field_name)
		else:
			return True
	
	# A method to determine whether or not the schema object has the necessary fields.
	@abstractmethod
	def check(self):
		raise NotImplementedError('AbstractDatum: This method should have been implemented by a sublcass')
	
	@abstractmethod
	def generate(self, rand):
		raise NotImplementedError('AbstractDatum: This method should have been implemented by a sublcass')

class StringDatum(AbstractDatum):
	values = []
	def __init__(self, field):
		AbstractDatum.__init__(self, field)
		self.check()
		#calculate CDF if necessary
		self.values = [] # list will be sorted by cumulative probability
		if type(self.field['values']) == dict:
			csum = 0
			for key in self.field['values']:
				prob = self.field['values'][key]
				csum += prob
				entry = {}
				entry['key'] = key
				entry['prob'] = csum
				self.values.append(entry)			
		
	def check(self):
		self.check_for_key('type')
		self.check_for_key('values')
		assert (self.field['type'] == 'string')
		val_type = type(self.field['values'])  
		assert (val_type == list or val_type == dict)
		
	def generate(self, rand):
		if type(self.field['values']) == list:
			num_items = len(self.field['values'])
			index = rand.randint(0, num_items - 1)
			return self.field['values'][index]
		elif type(self.field['values']) == dict:
			val = random.random()
			for i in range(len(self.values)):
				if val < self.values[i]['prob']:
					return self.values[i]['key']			
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	