import twint

c = twint.Config()
#c.Username = "batuhantosun"
c.Search = "@batuhantosun"
c.Elasticsearch = "http://localhost:9200"
c.Since = "2020-10-03"

#c.Store_csv=True
#c.Output="reply2.csv"
twint.run.Search(c)
