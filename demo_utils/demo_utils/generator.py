import json, config, random
from abc import abstractmethod
from logs import Logger

logger = Logger('Generator').getLogger()


class DataGenerator():
	
	def __init__(self, schema, seed=''):
		self.rand = random.Random()
		self.data_fields = []
		self.field_names = []
		self.schema = schema
		if not seed == '':
			self.rand.seed(seed)
			logger.info('Using seed: ' + seed)
		self.check_schema(schema)
		logger.info('Generator using Schema at: ' + str(schema))
				
	# Returns true/false whether or not the schema is valid
	# Raises an exception?
	def check_schema(self, schema):
		path = config.get_conf_dir() + schema

		with open(path) as data_file:
			conf = json.load(data_file)
			
			if not type(conf) == list:
				logger.error('JSON Schema not formatted properly')
				raise TypeError('Root of JSON Schema is not a list')
			
			for field in conf:
				if not 'fieldName' in field:
					logger.error('fieldName not found in schema at ' + path)
					raise KeyError('Could not find \'fieldName\' in field of schema: ' + schema )
					
				if not 'type' in field:
					logger.error('type not found in schema at ' + path)
					raise KeyError('Could not find \'type\' in field of schema: ' + schema)
				
				
				field_type = field['type']
				logger.debug('Attempting to register datum with type: ' + str(field_type))
				datum = AbstractDatum(field)
				if not datum.field_name in self.field_names:
					self.field_names.append(datum.field_name)
					logger.debug('Added datum to field set with type: ' + str(field_type))
				else:
					raise ValueError('Cannot have duplicate field names')
				if 'string' == field_type:
					datum = StringDatum(field)
				elif 'int' == field_type:
					datum = IntDatum(field)
				elif 'decimal' == field_type:
					datum = DecimalDatum(field)
				elif 'map' == field_type:
					datum = MapDatum(field)
				elif 'boolean' == field_type:
					datum = BooleanDatum(field)
				else:
					raise RuntimeError('Field type was not found. Please change the field type or implement a new datum')
				
				datum.check() # Check to make sure the field has necessary attributes	
				logger.info('Datum passed check successfully')
				self.data_fields.append(datum)
		
	def generate(self):
		data = {}
		maps = []
		for datum in self.data_fields:
			if datum.type == 'map':
				maps.append(datum)
				continue # put off mappers until end
			
			val = datum.generate(self.rand)
			
			data[datum.field_name] = val
			
		for mapper in maps:
			val = mapper.generate(self.rand, data)
			data[mapper.field_name] = val
		
		return data


class AbstractDatum(object):
		
	def __init__(self, field):
		self.field = field
		self.check_for_key('fieldName')
		self.check_for_key('type')
		self.field_name = field['fieldName']
		self.type = field['type']
		
	
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
	def __init__(self, field):
		self.values = []
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

class NumberDatum(AbstractDatum):
	def __init__(self, field):
		AbstractDatum.__init__(self, field)
		self.check()			
		
	def check(self):
		self.check_for_key('type')
		self.check_for_key('distribution')
		assert (self.field['type'] == 'int' or self.field['type'] == 'decimal')
		val_type = type(self.field['distribution'])  
		assert val_type == str or val_type == unicode
		d_type = self.field['distribution']
		if not (d_type == 'uniform' or d_type == 'exponential' or d_type == 'gaussian' or d_type == 'gamma'):
			raise ValueError('Distribution can only be one of: uniform, exponential, gaussian, or gamma')
		
		self.a = 0
		self.b = 1
		self.lambd = 1
		self.mu = 0
		self.sigma = 1
		self.alpha = 1
		self.beta = 1
		
		
		if 'a' in self.field:
				self.a = self.field['a']
		if 'b' in self.field:
				self.b = self.field['b']
		if 'lambda' in self.field:
				self.lambd = self.field['lambda']
		if 'mu' in self.field:
				self.mu = self.field['mu']
		if 'sigma' in self.field:
				self.sigma = self.field['sigma']
		if 'alpha' in self.field:
				self.alpha = self.field['alpha']
		if 'beta' in self.field:
				self.beta = self.field['beta']
		
		
		
	def generate(self, rand):
		distribution = self.field['distribution']
		num = 0
		if distribution == 'uniform':
			num = rand.uniform(self.a, self.b)
		elif distribution == 'exponential':
			num = rand.expovariate(self.lambd)
		elif distribution == 'gaussian':
			num = rand.gauss(self.mu, self.sigma)
		elif distribution == 'gamma':
			num = rand.gammavariate(self.alpha, self.beta)
			
		return num

class DecimalDatum(NumberDatum):
	def __init__(self, field):
		NumberDatum.__init__(self, field)
		
class IntDatum(NumberDatum):
	
	def __init__(self, field):
		NumberDatum.__init__(self, field)
		
	def generate(self, rand):
		return int(round(NumberDatum.generate(self, rand)))

class MapDatum(AbstractDatum):
	
	def __init__(self, field):
		AbstractDatum.__init__(self, field)
		self.field = field
		self.check()
	
	def check(self):
		self.check_for_key('map')
		self.check_for_key('mapFromField')
		if not type(self.field['map']) == dict:
			raise ValueError('Expected map key to be a dict object')
		if not (type(self.field['mapFromField']) == str or type(self.field['mapFromField']) == unicode):
			raise ValueError('Expected mapFromField key to be a dict object')
			
		self.maps = self.field['map']
		self.map_from = str(self.field['mapFromField'])
		
	def generate(self, rand, data):
		
		if not self.map_from in data:
			raise ValueError('Could not get key: ' + self.map_from + ' in data')
			
		key = data[self.map_from] # Get data from the map_from field
		
		try:
			return self.maps[key] # Get the mapped value from the given key
		except KeyError as e:
			return ''
class BooleanDatum(AbstractDatum):
	
	def __init__(self, field):
		AbstractDatum.__init__(self, field)
		self.field = field
		self.check()
		# Create CDF
		if 'values' in self.field:
			self.cdf_cutoff = self.field['values']['True']
		else:
			self.cdf_cutoff = 0.5
	
	def check(self):
		if 'values' in self.field:
			assert type(self.field['values']) == dict
			vals = self.field['values']
			assert 'True' in vals, 'True must in values'
			assert 'False' in vals, 'False must in values'
			assert vals['True'] + vals['False'] == 1.0, 'Probabilities must equal 1.0'
			
		
	def generate(self, rand):
		val = rand.random()
		if val < self.cdf_cutoff:
			return True
		else:
			return False
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	
	