import scrapy
import logging
from crawl_taylorandfrancis.items import CrawlTaylorandfrancisItem
import time


class TandfonlineSpider(scrapy.Spider):
    name = 'tandfonline'
    allowed_domains = ['tandfonline.com']
    # start_urls = ['http://tandfonline.com/']

    def start_requests(self):
        urls = [
            'https://www.tandfonline.com/action/showPublications?pubType=journal&alphabetRange={}'.format(chr(i+97)) for i in range(26)
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)
        # yield scrapy.Request(url="https://www.tandfonline.com/action/showPublications?pubType=journal&alphabetRange=a", callback=self.parse)

    def parse(self, response):
        # Redirect to journal information page
        info_links = response.xpath(
            '//a[@class="ref"]/@href').getall()
        for info_link in info_links:
            journal_code = info_link.split('/')[2]
            time.sleep(1)
            print("-------------------------info_link------------------------------")
            yield response.follow('https://www.tandfonline.com/action/journalInformation?show=journalMetrics&journalCode={}'.format(journal_code), callback=self.parse_journal)

        # Next page in list journal page
        next_page = response.xpath(
            '//a[@class="nextPage  js__ajaxSearchTrigger"]/@href').get()
        if next_page != None:
            time.sleep(1)
            yield response.follow(next_page, self.parse)

    def parse_journal(self, response):
        item = CrawlTaylorandfrancisItem()

        item['title'] = response.xpath(
            '//span[@class="journal-heading"]/a/text()').get().strip()

        impact_factor = response.xpath(
            '//div[@class="citation-metrics"]/ul/li[text()[contains(., "Impact Factor")]]/strong/text()').get()
        if impact_factor != None:
            item['impact_factor'] = impact_factor.strip().split(" ")[0]

        fyif = response.xpath(
            '//div[@class="citation-metrics"]/ul/li[text()[contains(., "5 year IF")]]/strong/text()').get()
        if fyif != None:
            item['fyif'] = fyif.strip().split(" ")[0]

        item['stfd'] = response.xpath(
            '//div[@class="speed"]/ul/li[text()[contains(., "from submission to first decision")]]/strong/text()').get()

        yield item
