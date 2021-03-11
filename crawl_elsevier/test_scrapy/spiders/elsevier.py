from test_scrapy.items import TestScrapyItem
import scrapy
import logging


class Elsevier(scrapy.Spider):
    name = "elsevier"
    allowed_domains = ["elsevier.com"]
    # start_urls = [
    #     "https://www.elsevier.com/catalog?producttype=journals",
    # ]

    def start_requests(self):
        urls = self.get_url()
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
        # yield scrapy.Request(url="https://www.elsevier.com/catalog?producttype=journals&page=134", callback=self.parse)

    def get_url(self):
        page = 138
        urls = [
            'https://www.elsevier.com/catalog?producttype=journals&page={}'.format(i+1) for i in range(138)
        ]
        return urls

    def parse(self, response):
        info_links = response.xpath(
            '//main/section[@class="listing-content clearfix"]/div[@class="listing-section-products clearfix"]/div/div[2]/div/a/@href'
        ).getall()

        for info_link in info_links:
            # logging.info(info_link)
            yield response.follow(info_link, callback=self.parse_journal)

    def parse_journal(self, response):
        item = TestScrapyItem()

        item['issn'] = response.xpath(
            '//div[@id="Title"]//div[@class="issn keyword"]/span/text()').get()
        item['title'] = response.xpath(
            '//div[@id="Title"]//h1[@itemprop="name"]/text()').get()
        item['fyif'] = response.xpath(
            '//div[@id="LeftCol1"]/div[@class="menu-item"]/div[1]/ul/li[text()[contains(., "5-Year Impact Factor")]]/span/b/text()').get()
        item['impact_factor'] = response.xpath(
            '//div[@id="Title"]//div[@class="publication"]//div[@class="publication-metrics"]//a[@aria-controls="publicationMetricTooltipImpactFactor"]/b/text()').get()
        item['stfd'] = response.xpath(
            '//div[@id="Title"]//div[@class="publication"]//div[@class="publication-metrics"]//a[@aria-controls="publicationMetricTooltipTtfdWeeks"]/b/text()').get()
        # item['editors'] = response.xpath(
        #     '//div[@id="Title"]//div[@class="publication-editors"]/span[@class="nowrap"]/text()').get()

        # logging.info(item)

        yield item
