
from elasticsearch import Elasticsearch
from django.shortcuts import redirect,reverse
from elasticsearch_dsl import Search, Q
from elasticsearch_dsl.query import SimpleQueryString
import datetime
import twint

class SearchElk():
    def __init__(self):
        self.client = Elasticsearch(['http://tw_elasticsearch'])

    def search(self,query="uitsec",default_operator="AND",tarih=10000,fields=["tweet^3","search^2"],exact_tarih=None):
        
        tarih_range = (datetime.datetime.now() - datetime.timedelta(days=tarih)).strftime("%Y-%m-%d %H:%M:%S")
        if exact_tarih:
            tarih_range = exact_tarih
        search_kelimeler = query.split(" ")
        query_orjinal = ""
        query_tr = ""
        
        for kelime in search_kelimeler:
            kelime_tr_uygun = self.kelimeTr(kelime)

                    # last_imp = "(\""+kelime+"\"~2)"
            query_tr += " "+kelime_tr_uygun
            query_orjinal += " "+ kelime
        query_near = "(\""+query_orjinal[1:]+"\"~3)"+"|"+"(\""+query_tr[1:]+"\"~3)"
       # print(tarih_range,query,fields,default_operator)
        
        s = Search(using=self.client, index="twinttweets")
        
        
        if len(search_kelimeler)<2:
            print("urdas")
            try:
                
                 s = s.filter(SimpleQueryString(
                             query=query_tr+"|"+query_orjinal,
                             fields=fields,
                             default_operator=default_operator
                 ))[:10000]
                #s = s.filter(SimpleQueryString(query="%s"%query),fields=fields,default_operator=default_operator)[:10000]
            except Exception as e:
                print("elasticsearch.py 45 error",e)
        else:
            
            q = Q('bool',
                must=[Q('function_score',boost_mode='sum',query=Q('simple_query_string',query=query_near,
                fields=['tweet','search'],minimum_should_match='85%',default_operator='OR')),
                Q('function_score',boost_mode='sum',query=Q('simple_query_string',query=query_near,
                fields=['tweet','search'],minimum_should_match='85%',default_operator='OR'))])
            s = s.query(q)[:10000]
        
        print(query_orjinal,query_tr,query_near,fields)
        # ESKİ SEARCH #
        # s = s.filter(SimpleQueryString(
        #             query=query_near,
        #             fields=fields,
        #             default_operator=default_operator
        # ))[:10000]
        
        s = s.filter('range',**{'date':{'gte':tarih_range}})
        # s = s.sort('-date')
        response = s.execute()
        #print('Total %d hits found.' % response.hits.total)
        
        search = self.get_results(response)
        #print(type(search[0]))
        return search
    def kelimeTr(self,keyword):
        x = "ıöüğçş"
        y = "iougcs"
        temp = keyword.maketrans(x,y)
        return keyword.translate(temp)
    def customSearch4Alert(self,query,tarih,default_operator="or",fields=["tweet^4","hashtags","username","name","link"]):
        s = Search(using=self.client, index="twinttweets")
        # s = s.query(SimpleQueryString(
        #     query="%s"%query,
        #     fields=fields,
        #     default_operator=default_operator
        # ))[:10000]
        q = Q('bool',
            must=[],
            must_not=[],
            should=[Q('function_score',boost_mode='sum',query=Q('simple_query_string',query="batuhantosun",fields=['tweet','search'],minimum_should_match='85%',default_operator='OR')),
            Q('function_score',boost_mode='sum',query=Q('simple_query_string',query="(\"batuhan tosun\"~2)",fields=['tweet','search'],minimum_should_match='85%',default_operator='OR'))])
                
        s = s.filter('range',**{'date':{'gte':tarih}})
        response = s.execute()
        search = self.get_results(response)
        return search
    def get_results(self,response):
        results = []

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
    def get_count(self):
        #self.client.refresh("twinttweets")
        self.client = Elasticsearch(['http://tw_elasticsearch'])
        json_res = self.client.count(index="twinttweets")
        return json_res["count"]



class InsertElk():
    def __init__(self):
        self.c = twint.Config()
        self.c.Elasticsearch = "http://tw_elasticsearch:9200"
    def runOnce(self,keyword):
        self.c.Search = keyword
        twint.run.Search(self.c)
    def runScheduled(self,keyword,since=None):
        self.c.Search = keyword
        if since:
            self.c.Since = since
        twint.run.Search(self.c)

            
            
