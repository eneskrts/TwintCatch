import twint

from elasticsearch import Elasticsearch
from django.shortcuts import redirect,reverse
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import SimpleQueryString
import datetime
import twint
class SearchElk():
    def __init__(self):
        self.client = Elasticsearch()
    def search(self,query="uitsec batuhan",default_operator="and",tarih=10000,fields=["tweet^4","hashtags","username","name","link"]):
        tarih_range = (datetime.datetime.now() - datetime.timedelta(days=tarih)).strftime("%Y-%m-%d %H:%M:%S")
       # print(tarih_range,query,fields,default_operator)
        #client = Elasticsearch()
        s = Search(using=self.client, index="twinttweets")
        s = s.filter(SimpleQueryString(
            query="%s"%query,
            fields=fields,
            default_operator=default_operator
        ))[:10000]
        s = s.filter('range',**{'date':{'gte':tarih_range}})
        response = s.execute()
        #print('Total %d hits found.' % response.hits.total)

        search = self.get_results(response)
        #print(type(search[0]))
        return search

    def get_results(self,response):
        results = []
        print(len(response))
        print("VALUE",response)
        if len(response) < 1 :
            return (0)
        for hit in response:
            hit_dict  = hit.to_dict()
            # result_tuple = (hit.tweet)
            if len(hit_dict.get("tweet"))<3:
                continue
            results.append(hit_dict)
        #print(type(hit),response[0].to_dict())
        return results

# c = twint.Config()
# c.Search = "uitsec"
# c.Elasticsearch = "http://127.0.0.1:9200"

# twint.run.Search(c)
#print(res)
se = SearchElk()
test = se.search(query="uitsec enes")
#print(test)