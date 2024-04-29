
from elasticsearch import Elasticsearch
from django.conf import settings
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import SimpleQueryString
import datetime
import twint


class SearchElk():
    def __init__(self):
        es_host = getattr(settings, "ELASTICSEARCH_HOST", "http://localhost:9200")
        self.client = Elasticsearch([es_host])

    def search(self, query="uitsec", default_operator="AND",
               tarih=10000, fields=("tweet^3", "search^2"),
               exact_tarih=None):
        tarih_range = (datetime.datetime.now() - datetime.timedelta(days=tarih)).strftime("%Y-%m-%d %H:%M:%S")
        if exact_tarih:
            tarih_range = exact_tarih
        search_kelimeler = query.split(" ")
        query_orjinal = ""
        query_tr = ""
        
        for kelime in search_kelimeler:
            kelime_tr_uygun = self.kelimeTr(kelime)

            query_tr += " "+kelime_tr_uygun
            query_orjinal += " " + kelime
        query_near = "(\""+query_orjinal[1:]+"\"~3)"+"|"+"(\""+query_tr[1:]+"\"~3)"

        s = Search(using=self.client, index="twinttweets")
        s = s.execute()
        print(s.to_dict())
        """
        if len(search_kelimeler)<2:
            try:
                 s = s.filter(SimpleQueryString(
                             query="another",
                             fields=fields,
                             default_operator=default_operator
                 ))[:10000]
            except Exception as e:
                print("elasticsearch.py 45 error",e)
        else:
            
            q = Q('bool',
                must=[Q('function_score',boost_mode='sum',query=Q('simple_query_string',query=query_near,
                fields=['tweet','search'],minimum_should_match='85%',default_operator='OR')),
                Q('function_score',boost_mode='sum',query=Q('simple_query_string',query=query_near,
                fields=['tweet','search'],minimum_should_match='85%',default_operator='OR'))])
            s = s.query(q)[:10000]

        s = s.filter('range',**{'date':{'gte':tarih_range}})
        """
        #response = s.execute()

        search = self.get_results(s)
        print("sdasdasdasd", search)
        return search

    def kelimeTr(self,keyword):
        x = "ıöüğçş"
        y = "iougcs"
        temp = keyword.maketrans(x,y)
        return keyword.translate(temp)

    def customSearch4Alert(self,query,tarih, default_operator="or",fields=["tweet^4","hashtags","username","name","link"]):
        s = Search(using=self.client, index="twinttweets")

        q = Q('bool',
              must=[],
              must_not=[],
              should=[Q('function_score', boost_mode='sum',
                      query=Q('simple_query_string', query=query, fields=['tweet', 'search'],
                              minimum_should_match='85%', default_operator=default_operator)),
                    Q('function_score', boost_mode='sum', query=Q('simple_query_string',
                                                                  query=f"(\"{query}\"~2)",
                                                                  fields=['tweet', 'search'],
                                                                  minimum_should_match='85%',
                                                                  default_operator='OR'))])
                
        s = s.filter('range', **{'date': {'gte': tarih}})
        response = s.execute()
        search = self.get_results(response)
        return search

    def get_results(self,response):
        results = []

        if len(response) < 1:
            return (0)
        for hit in response:
            hit_dict = hit.to_dict()
            hit_dict["tweet"] =hit_dict["tweet_text"]
            results.append(hit_dict)
        return results

    def get_count(self):
        es_host = getattr(settings, "ELASTICSEARCH_HOST", "http://localhost:9200")
        self.client = Elasticsearch([es_host])
        json_res = self.client.count(index="twinttweets")
        return json_res["count"]


class InsertElk():
    def __init__(self):
        self.c = twint.Config()
        es_host = getattr(settings, "ELASTICSEARCH_HOST", "http://localhost:9200")
        self.c.Elasticsearch = es_host

    def runOnce(self,keyword):
        self.c.Search = keyword
        twint.run.Search(self.c)

    def runScheduled(self,keyword,since=None):
        self.c.Search = keyword
        if since:
            self.c.Since = since
        twint.run.Search(self.c)

            
            
