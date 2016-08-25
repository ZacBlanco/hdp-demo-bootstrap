import unittest, json, mock, env
from mock import Mock

import cluster, time, demo_utils
from cluster import ThreadedGenerator
from demo_utils.generator import DataGenerator

test_config = '''[{"fieldName":"string_data","type":"string","values":{"a":0.1,"b":0.9}},{"fieldName":"int_data","type":"int","distribution":"uniform"},{"fieldName":"float_data","type":"decimal","valuesA":["a","b","c","d"],"distribution":"gaussian"},{"fieldName":"boolean_data","type":"boolean","values":{"True":0.7,"False":0.3}},{"fieldName":"map_data","mapFromField":"string_data","type":"map","map":{"a":"c","b":"d"}}]'''


class TestClusterFuncs(unittest.TestCase):
  
  def test_hive_queries(self):
    q = cluster.generate_queries(test_config)
    cfg = json.loads(test_config)
    fields = map(lambda d: str(d['fieldName']), cfg)
    r = map(lambda x: x in q['HIVE']['Basic Table'], fields)
    if False in r:
      self.fail('Not all fields present in basic hive table creation')
    
    
    
    
    
    
    
  @mock.patch('kafka.KafkaProducer', return_value='')
  def test_threaded_hdfs_write(self, mock1):
    
    dg = DataGenerator(test_config)
    data = []
    for i in range(11):
      data.append(dg.generate())
    
    gen = ThreadedGenerator(test_config, 10, ["HDFS"], 10);
    gen.hdfs_data_pool = data
    gen.export_hdfs({})
    assert gen.hdfs_data_pool == [], 'Data pool should be empty'