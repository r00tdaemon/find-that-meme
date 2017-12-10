# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html

from bson.binary import Binary
import io
import re

from PIL import Image
import pymongo
import pytesseract
import scrapy.exceptions
from nltk.corpus import stopwords
from textblob import TextBlob


def process_image(img):
    img = Image.open(io.BytesIO(img))
    img = img.convert('L')
    img = img.point(lambda x: 0 if x < 245 else 255, '1')
    text = pytesseract.image_to_string(img, config='--tessdata-dir ../', lang='eng')
    text = re.sub(r"\s+", " ", text)
    text = TextBlob(text.lower()).correct()
    text = [word for word in text.split() if word not in set(stopwords.words('english'))]
    return text


class MemeScrapyPipeline(object):
    collection_name = 'memes'

    def __init__(self, mongo_uri, mongo_db):
        self.mongo_uri = mongo_uri
        self.mongo_db = mongo_db

    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            mongo_uri=crawler.settings.get('MONGO_URI'),
            mongo_db=crawler.settings.get('MONGO_DATABASE')
        )

    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.mongo_uri)
        self.db = self.client[self.mongo_db]

    def close_spider(self, spider):
        self.client.close()

    def process_item(self, item, spider):
        text = process_image(item["img"])
        if text:
            doc = dict(item)
            doc["img"] = Binary(item["img"])
            doc["description"] = item["meme_type"].lower().split("-") + text
            self.db[self.collection_name].insert_one(doc)
        else:
            item.pop("img")
            raise scrapy.exceptions.DropItem("Image does not contain recognizable text")
        return item
