import bs4, requests, rss, elasticsearch, certifi, configparser, os

def read_conf(ini):
    conf_file = configparser.ConfigParser()
    conf_file.read_file(open(ini))
    return conf_file

def get_es_url_from_conf(conf):
    es = conf["es"]
    host, port, user, pw = es["host"], es["port"], es["user"], es["pass"]
    return f"https://{user}:{pw}@{host}:{port}"

ini = "db.ini"

# email Zach for the INI file
if not os.path.isfile(ini):
    print("INI file is missing. Email Zach.")
    quit()

# create connection to Elasticsearch using INI settings
conf = read_conf(ini)
es_url = get_es_url_from_conf(conf)
es = elasticsearch.Elasticsearch([es_url])
es.index_name = conf["es"]["index"]

# hard coded for now; can be replaced with sys arg
test_url = "https://globenewswire.com/Rss/industry/1771/Coal"

# scrape the RSS feed
response = requests.get(test_url)
content = response.text 
soup = bs4.BeautifulSoup(content, "xml")
soup_items = soup.find_all("item")
rss_items = [rss.Item(item) for item in soup_items]

# update Elasticsearch with new items
es_update = [item.add_to(es) for item in rss_items]

# delete index from Elasticsearch
# es.indices.delete(index=es.index_name)
