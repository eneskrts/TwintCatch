from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import SimpleQueryString,FunctionScore
import datetime

client = Elasticsearch(maxsize=10000)
s = Search(using=client,index="twinttweets")
s2 = {
  "query":{
    "bool": {
      "must": [
        
      ], 
      "must_not": [
      ], 
      "should": [
        {
          "function_score": {
            "query": {
              "simple_query_string": {
                "query": "(\"batuhan tosun\"~3)",
                "fields": ["tweet","search"],
                "minimum_should_match":"75%",
                "default_operator": "OR"
              }
            },
            "boost_mode": "sum"
          }
            
          },
          {
            "function_score": {
              "query": {
                "simple_query_string": {
                  "query": "batuhantosun",
                  "fields": ["tweet","search"],
                  "minimum_should_match":"75%",
                  "default_operator": "OR"
                }
              },
             
              "boost_mode": "sum"

            }
          }
        
      ]
    }
  }
}
print(set(s2))
sample_func_score = {
            "function_score": {
              "query": {
                "simple_query_string": {
                  "query": "batuhantosun",
                  "fields": ["tweet","search"],
                  "minimum_should_match":"75%",
                  "default_operator": "OR"
                }
              },
             
              "boost_mode": "sum"

            }
          }
res = client.search(index="twinttweets",body=s2,size=10)
c = 0
for hit in res["hits"]["hits"]:
    #print(hit)
    c+=1
print(c)
import itertools
words = ["batuhan","tosun","uitsec"]
combinations = list(itertools.combinations(words,2))
func_score_arr = []
for comb in combinations:
    pass

# print(len(res))
q = Q('bool',
    must=[],
    must_not=[],
    should=[Q('function_score',boost_mode='sum',query=Q('simple_query_string',query="batuhantosun",fields=['tweet','search'],minimum_should_match='85%',default_operator='OR')),
    Q('function_score',boost_mode='sum',query=Q('simple_query_string',query="(\"batuhan tosun\"~2)",fields=['tweet','search'],minimum_should_match='85%',default_operator='OR'))])
    



s = s.query(q)[:10000]

res = s.execute()
print(len(res))

#print(res[0].to_dict())
#print(len(res))
for hit in res[:10]:
    print(hit.to_dict().get("tweet"))
    pass