'''The module which houses the data generator and all of the different types of Datum Objects.

This module is easily extendable by simple implementing the methods in the AbstractDatum class.

Configurations can be read through JSON strings or JSON files.

A configuration object itself should be a list of JSON objects. Each JSON object should have at least two fields implemented

  - ``fieldName`` (str): A simple user-defined name for this field
  - ``type`` (str): A Datum which has been implemented in the data generator
  
Any other properties of the object are specific to the type of datum (see datum documentation below).

Example:
  .. code-block:: python
    :linenos:

    import demo_utils.generator
    from generator import DataGenerator

    rand_schema = '/path/to/schema.json'
    # or
    # import json
    # js_schema = [
    #               {
    #                 "fieldName": "field1"
    #                 "type": "string"
    #                 "values": ["a", "b", "c", "d"]
    #               }
    #             ]
    # rand_schema = json.dumps(js_schema)


    gen = DataGenerator(rand_schema)
    # Generate a single 'row' of data
    print(gen.generate())


'''
#!/usr/bin/python
# -*- coding: utf-8 -*-

import json
import config
import random
from abc import abstractmethod
from logs import Logger

logger = Logger('Generator').getLogger()


class DataGenerator:
  '''The generator object. Pass the configuration here. use the generate() method to get a random object
  
  Args:
    schema (str): The schema file or JSON string which defines the data to be generated.
    seed (str, optional): The seed value for the generator
  
  '''

  def __init__(self, schema, seed=''):
    self.rand = random.Random()
    self.data_fields = []
    self.field_names = []
    self.schema = schema
    if not seed == '':
      self.rand.seed(seed)
      logger.info('Using seed: ' + seed)
    self.check_schema(schema)
    if self.using_file:
      logger.info('Generator using Schema at: ' + str(schema))

# Returns true/false whether or not the schema is valid
# Raises an exception?

  def check_schema(self, schema):
    '''Checks the entire schema for any incorrect or missing parameters.
    
    Args:
      schema (str): The file path or JSON string of the schema
    
    Returns:
      N/A
      
    Raises:
      TypeError: If the root of JSON schema is not a list.
      KeyError: If 'fieldName' or 'type' are not found in a datum
      ValueError: If there are duplicate fieldNames
      RuntimeError: If a certain 'type' isn't found
      
    '''
    conf = None
    try:
      path = config.get_path(schema)
      with open(path) as df:
        conf = json.load(df)
#        logger.info('Successfully read config from file')
      self.using_file = True
    except IOError:
      self.using_file = False
      logger.info('Could not read schema as file. Attempting to read as JSON string')
      pass

    if conf == None:
        conf = json.loads(schema)
        logger.info('Read as JSON string')

    if not type(conf) == list:
      logger.error('Root of JSON Schema is not a list')
      raise TypeError('Root of JSON Schema is not a list')

    for field in conf:
      if not 'fieldName' in field:
        logger.error('fieldName not found in schema')
        raise KeyError('Could not find \'fieldName\' in field of schema')
      if not 'type' in field:
        logger.error('type not found in schema')
        raise KeyError('Could not find \'type\' in field of schema')
      field_type = field['type']
      datum = AbstractDatum(field)
      if not datum.field_name in self.field_names:
        self.field_names.append(datum.field_name)
        logger.debug('Added datum to field set with type: '
                     + str(field_type))
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
        raise RuntimeError('Field type:' + field_type + ' was not found. Please change the field type or implement a new datum')
      # Check to make sure the field has necessary attributes
      datum.check()
      self.data_fields.append(datum)

  def generate(self):
    '''Produce a single row of data. One random value for each datum.
    
    Returns:
      (dict): A dictionary object with keys for each fieldName in the schema. Values according to the schema.
      
    '''
    data = {}
    maps = []
    for datum in self.data_fields:
      if datum.type == 'map':
        maps.append(datum)
        continue  # put off mappers until end
      val = datum.generate(self.rand)
      data[datum.field_name] = val
    for mapper in maps:
      val = mapper.generate(data)
      data[mapper.field_name] = val
    return data


class AbstractDatum(object):
  '''An abstract object which defines some methods for other Datum to implement.
  
  This class should NOT be instantiated
  '''

  def __init__(self, field):
    self.field = field
    self.check_for_key('fieldName')
    self.check_for_key('type')
    self.field_name = field['fieldName']
    self.type = field['type']

  def check_for_key(self, key_name):
    '''Ensure the key is in the field
    
    Args:
      key_name (str): The key to check for in the datum object
      
    Returns:
      bool: True if the key is in the object. Otherwise an error will be raised
      
    Raises:
      KeyError: If they key is not present, this error is raised.
    '''
    if not key_name in self.field:
      raise KeyError('Missing key: ' + key_name + ' in ' + self.field_name)
    else:
      return True

  # A method to determine whether or not the schema object has the necessary fields.
  @abstractmethod
  def check(self):
    '''This method should not be used
    
    Raises:
      NotImplementedError: This method should not be called by an instance of this class. (In fact there should never be an instance of just this class)
      '''
    raise NotImplementedError('AbstractDatum: This method should have been implemented by a sublcass')

  @abstractmethod
  def generate(self, rand):
    '''This method should not be used
    
    Raises:
      NotImplementedError: This method should not be called by an instance of this class. (In fact there should never be an instance of just this class)
      '''
    raise NotImplementedError('AbstractDatum: This method should have been implemented by a sublcass')


class StringDatum(AbstractDatum):
  '''A datum that will randomly generate strings
  
  There are two possible options writing schemas.
  
  The first is using a list of strings. This causes each element to appear with equal probability.
  ::
  
    {
      "fieldName": "test_field",
      "type": "string",
      "values": ["a", "b", "c", "d"]
    }
    
    
  The second is using an object with different keys, and specifying a probability for each key.
  ::
  
    {
      "fieldName": "test_field",
      "type": "string",
      "values": {
        "a": 0.1,
        "b": 0.2,
        "c": 0.5
      }
    }
    
  
  
  Args:
    field (dict): The datum object (represented as a dict)
    
  '''
  

  def __init__(self, field):
    self.values = []
    AbstractDatum.__init__(self, field)
    self.check()
    #    calculate CDF if necessary
    self.values = []  # list will be sorted by cumulative probability
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
    '''Ensure that the fieldName and values are proper. 
    
    Shouldn't be called externally
    '''
    self.check_for_key('type')
    self.check_for_key('values')
    assert self.field['type'] == 'string'
    val_type = type(self.field['values'])
    assert val_type == list or val_type == dict

  def generate(self, rand):
    '''Generate a string from the given list of values. Pick one based on even or given probabilities
    
    Shouldn't be called externally
    '''
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
  '''Create a random number form a schema object
  
  This datum shouldn't be used. Use the ``IntDatum`` or ``DecimalDatum`` instead.
  
  Along with 'fieldName' and 'type' a number datum requires a 'distribution' field. 
  
  There are 4 types of distributions currently available (along with the extra argument that can be supplied for each):
  
  Args:
    uniform: A distribution which produces numbers between a and b with equal probability.
    
      - ``a``: lower bound. Defaults to 0.
      - ``b``: upper bound. Defaults to 1.
      
    exponential: A distribution which produces lower values with high probability.
    
      - ``lambda``: Lower values (greater than 0) results in higher numbers. High values of lambda result in lower values. Defaults to 1.
      
    gaussian: A distribution which produces numbers in a normal curve. The values produced will fall in between 3 standard deviations 97% of the time.
    
      - ``mu``: The mean of all numbers which will be produced. Defaults to 0.
      - ``sigma``: The standard deviation of numbers produced. Defaults to 1.
    gamma: Results in a gamma distribution
      
      - ``alpha``: defaults to 1
      - ``beta``: defaults to 1
      
  Example:
  
    Gaussian Example:
    ::

      {
        "fieldName": "number_field",
        "type": "int",
        "distribution": "gaussian",
        "mu": 50,
        "sigma": 10
      }
      
      
    Exponential Example
    ::

      {
        "fieldName": "number_field",
        "type": "decimal",
        "distribution": "exponential",
        "lambda": 0.5
      }
  '''
  
  def __init__(self, field):
    AbstractDatum.__init__(self, field)
    self.check()

  def check(self):
    '''Not to be used externally'''
    self.check_for_key('type')
    self.check_for_key('distribution')
    assert self.field['type'] == 'int' or self.field['type'] \
        == 'decimal'
    val_type = type(self.field['distribution'])
    assert val_type == str or val_type == unicode
    d_type = self.field['distribution']
    if not (d_type == 'uniform' or d_type == 'exponential'
            or d_type == 'gaussian' or d_type == 'gamma'):
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
    '''Generates a rando number based on the distribution parameters given in the schema.'''
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
  '''The DecimalDatum uses the NumberDatum to generate numbers. It does not truncate any decimal places.
  
  For configuration examples please see the documentation on ``NumberDatum``
  
  '''
  def __init__(self, field):
    NumberDatum.__init__(self, field)

class IntDatum(NumberDatum):
  '''The IntDatum uses the NumberDatum to generate numbers. It Rounds to the nearest whole and then convert the number to an int before returning .
  
  For configuration examples please see the documentation on ``NumberDatum``
  '''
  def __init__(self, field):
    NumberDatum.__init__(self, field)

  def generate(self, rand):
    return int(round(NumberDatum.generate(self, rand)))
  
  
class MapDatum(AbstractDatum):
  '''Allows you to Map certain values from one field to another.
  
  Using two special fields: ``map`` and ``mapFromField`` you can use this field to generate a certain piece of data based on another field's value. Must be a string.
  
  Example:
  ::
    
    {
      "fieldName": "mapped_field",
      "type": "map",
      "mapFromField": "RandomIntField1",
      "map": {
        "1": "small",
        "2": "small",
        "3": "small",
        "4": "small",
        "5": "small",
        "6": "large",
        "7": "large",
        "8": "large",
        "9": "large",
        "10": "large"
      }
    }
    
  Another Example using gender:
  ::
  
    {
      "fieldName": "gender",
      "type": "map",
      "mapFromField": "fName",
      "map": {
        "Jen":    "F",
        "Susan":  "F",
        "Mary":   "F",
        "John":   "M",
        "Mike":   "M",
        "Joe":    "M"
      }
    }
  
  
  
  '''
  def __init__(self, field):
    AbstractDatum.__init__(self, field)
    self.field = field
    self.check()

  def check(self):
    '''Not to be used externally
    
    Checks to make sure the "map" and "mapFromField" are present in the datum
    
    '''
    self.check_for_key('map')
    self.check_for_key('mapFromField')
    if not type(self.field['map']) == dict:
      raise ValueError('Expected map key to be a dict object')
    if not (type(self.field['mapFromField']) == str or type(self.field['mapFromField']) == unicode):
      raise ValueError('Expected mapFromField key to be a dict object'
                         )
    self.maps = self.field['map']
    self.map_from = str(self.field['mapFromField'])

  def generate(self, data):
    '''Not to be used externally.
    
    Generates the data from the map
    '''
    if not self.map_from in data:
      raise ValueError('Could not get key: ' + self.map_from + ' in data')
    key = data[self.map_from]  # Get data from the map_from field
    try:
      return self.maps[str(key)]  # Get the mapped value from the given key
    except KeyError, e:
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


