import bs4, json, requests, elasticsearch

class RSS_Item:
    def __init__(self, soup_tag):
        self.link = soup_tag.link.text
        self.title = soup_tag.title.text
        self.pub_date = soup_tag.pubDate.text

    # Private method for converting object properties to JSON format.
    def __to_json(self):
        return json.dumps(self.__dict__)

    # This method allows an object to insert itself into a given elasticsearch db.
    def add_to_es(self, es, index="globenewswire", doc_type="rss"):
        res = es.index(index=index, doc_type=doc_type, body=self.__to_json())
        return res["created"]

test_url = "https://globenewswire.com/Rss/industry/1771/Coal"

response = requests.get(test_url)
# We start by making an HTTP request and storing the response as a Response object. 
# type(response): <class 'requests.models.Response'>
# The Response class has useful methods and properties, like the following...
content = response.text 
# This creates a string with the relevant RSS content. Now we just need to find the
# specific text content we care about. BUT parsing string content is a nightmare. Let's 
# stand on the shoulders of giants by using another third-party library.
soup = bs4.BeautifulSoup(content, "xml")
# Now we're dealing with a BeautifulSoup object, with tons of useful methods.
# type(soup): <class 'bs4.BeautifulSoup'>
# You can read more at https://www.crummy.com/software/BeautifulSoup/bs4/doc/
# but the most useful method is find_all()...
soup_tags = soup.find_all("item")
# This creates a list of BeautifulSoup tag objects, with their own set of useful methods,
# and also filters out all the unimportant text content from the original HTTP response.
# type(soup_tags): <class 'bs4.element.ResultSet'>
# type(soup_tags[1]): <class 'bs4.element.Tag'>
# Unfortunately third-party libraries can only help SO MUCH. It's time to convert these
# tag objects into a more useful form, such as the RSS_Item class I defined above.
rss_items = [RSS_Item(soup_tag) for soup_tag in soup_tags]
# type(rss_items[0]): <class '__main__.RSS_Item'>


# The following code block creates a connection to the local instance of elasticsearch and 
# then iterates through the rss_items list while running the add_to_es method. The exception 
# is in place for users who haven't set-up elasticsearch.
# 
# To set-up Elasticsearch in Debian:
# 1. wget https://artifacts.elastic.co/downloads/elasticsearch/elasticsearch-5.2.1.deb
# 2. sudo dpkg -i elasticsearch-5.2.1.deb
# 3. sudo systemctl start elasticsearch.service
# 4. curl http://localhost:9200/
#
# Useful commands:
# GET /_search?q=
# DELETE /<index>/<type>/<id>

try:
    es = elasticsearch.Elasticsearch()  # use default of localhost, port 9200
    es_update = [item.add_to_es(es) for item in rss_items]
except:
    print("Elasticsearch is not configured on this machine.")
