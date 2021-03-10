import scrapy
import logging
from scrapy_wiley.items import ScrapyWileyItem


class WileySpider(scrapy.Spider):
    name = 'wiley'
    allowed_domains = ['onlinelibrary.wiley.com']
    # start_urls = ['http://onlinelibrary.wiley.com/']

    def start_requests(self):
        # urls = [
        #     'https://onlinelibrary.wiley.com/action/showPublications?PubType=journal&alphabetRange={}'.format(chr(i+97)) for i in range(26)
        # ]
        # urls.append(
        #     'https://onlinelibrary.wiley.com/action/showPublications?PubType=journal&alphabetRange=0-9')
        # for url in urls:
        #     yield scrapy.Request(url=url, callback=self.parse)
        yield scrapy.Request("https://onlinelibrary.wiley.com/action/showPublications?PubType=journal&alphabetRange=a", callback=self.parse)

    def parse(self, response):
        # Redirect to journal information page
        info_links = response.xpath(
            '//ul[@class="rlist separator search-result__body titles-results"]/li//a[@class="visitable"]/@href').getall()
        for info_link in info_links:
            yield response.follow('https://onlinelibrary.wiley.com{}'.format(info_link), callback=self.parse_journal)

        # Next page in list journal page
        next_page = response.xpath(
            '//a[@title="Next page"]/@href').get()
        if next_page != None:
            yield response.follow(next_page, self.parse)

    def parse_journal(self, response):
        item = ScrapyWileyItem()

        info_label = response.xpath(
            '//div[@data-widget-def="graphQueryWidget"]/div/span[@class="info_label"]/text()'
        ).getall()
        info_value = response.xpath(
            '//div[@data-widget-def="graphQueryWidget"]/div/span[@class="info_value"]/text()'
        ).getall()

        for i, label in enumerate(info_label):
            if 'Online ISSN' in label:
                item['issn'] = info_value[i]
            elif 'Impact factor:' in label:
                item['impact_factor'] = info_value[i]

        item['title'] = response.xpath(
            '//meta[@property="og:title"]/@content'
        ).get()

        yield item
