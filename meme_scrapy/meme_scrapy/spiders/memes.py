from bson.binary import Binary
import scrapy

from meme_scrapy.items import MemeItem


class MemeSpider(scrapy.Spider):
    name = "memes"
    start_urls = [
        "https://imgflip.com/memetemplates",
        "https://imgflip.com/memetemplates?page=2",
        "https://imgflip.com/memetemplates?page=3",
        "https://imgflip.com/memetemplates?page=4",
        "https://imgflip.com/memetemplates?page=5",

    ]

    def parse(self, response: scrapy.http.Response):
        urls = response.xpath(
            "//div[@class='mt-img-wrap']/a[contains(@href, '/meme/')]/@href"
        ).extract()

        memes = response.xpath("//img[@class='base-img']/@src").extract()

        if memes:
            for meme in memes:
                yield scrapy.Request(
                    "https://{}".format(meme),
                    callback=self.get_image,
                    meta={"meme_type": response.url.split("/")[-1]}
                )

        for url in urls:
            yield response.follow(url, self.parse)

    def get_image(self, response: scrapy.http.Response):
        item = MemeItem()
        item["meme_type"] = response.meta.get("meme_type")
        item["img"] = Binary(response.body)
        yield item
