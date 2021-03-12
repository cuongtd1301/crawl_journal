from test_scrapy.items import TestScrapyItem
import scrapy
import logging


class Elsevier(scrapy.Spider):
    name = "elsevier"
    allowed_domains = ["elsevier.com"]

    def start_requests(self):
        page = 138
        urls = [
            'https://www.elsevier.com/catalog?producttype=journals&page={}'.format(i+1) for i in range(138)
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        info_links = response.xpath(
            '//div[@class="listing-product-links--inner"]/a/@href'
        ).getall()

        for info_link in info_links:
            yield response.follow(info_link, callback=self.parse_journal)

    def parse_journal(self, response):
        item = TestScrapyItem()

        issn = response.xpath(
            '//div[contains(@class, "issn")]/span/text()').get()
        if issn != None:
            item['issn'] = issn.replace("-", "").strip()
        # item['title'] = response.xpath(
        #     '//div[@id="Title"]//h1[@itemprop="name"]/text()').get()
        item['fyif'] = response.xpath(
            '//div[@id="LeftCol1"]/div[@class="menu-item"]/div[1]/ul/li[text()[contains(., "5-Year Impact Factor")]]/span/b/text()').get()
        item['impact_factor'] = response.xpath(
            '//div[@id="Title"]//div[@class="publication"]//div[@class="publication-metrics"]//a[@aria-controls="publicationMetricTooltipImpactFactor"]/b/text()').get()
        item['stfd'] = response.xpath(
            '//div[@id="Title"]//div[@class="publication"]//div[@class="publication-metrics"]//a[@aria-controls="publicationMetricTooltipTtfdWeeks"]/b/text()').get()

        yield item
