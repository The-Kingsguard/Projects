import json, elasticsearch

class Item:
    def __init__(self, soup_tag):
        self.link = soup_tag.link.text
        self.title = soup_tag.title.text
        self.pub_date = soup_tag.pubDate.text
        self.doc_type = "rss"

    # Private method for converting object properties to JSON format.
    def __to_json(self):
        return json.dumps({"link": self.link, "title": self.title, "pub_date": self.pub_date})

    def add_to(self, db):
        res = False
        if type(db) == elasticsearch.client.Elasticsearch:
            res = db.index(index=db.index_name, doc_type=self.doc_type, body=self.__to_json())
        return res
