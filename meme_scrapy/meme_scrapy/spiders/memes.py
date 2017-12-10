import scrapy

from meme_scrapy.items import MemeItem


class MemeSpider(scrapy.Spider):
    name = "memes"
    start_urls = [
        "https://imgflip.com/memetemplates?page={}".format(x) for x in range(1, 6)
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

        # next_page = response.xpath("//a[@class='pager-next']/@href").extract_first()
        # if next_page and "/meme/" in response.url:
            # urls.append(next_page)

        for url in urls:
            yield response.follow(url, self.parse)

    def get_image(self, response: scrapy.http.Response):
        item = MemeItem()
        item["url"] = response.url
        item["meme_type"] = response.meta.get("meme_type")
        item["img"] = response.body
        yield item
