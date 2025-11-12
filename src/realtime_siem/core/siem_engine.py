# In src/realtime_siem/core/siem_engine.py
def connect_to_elasticsearch(self):
    from elasticsearch import Elasticsearch
    self.es = Elasticsearch([
        {'host': self.config.get('elasticsearch.host'), 
         'port': self.config.get('elasticsearch.port')}
    ])