from training_scrapy.items import JournalMetric
import scrapy
import logging


class SpingerSpider(scrapy.Spider):
    name = 'springer'
    allowed_domains = ["springer.com"]
    # start_urls = [
    #     'https://link.springer.com/journals/a/1'
    # ]

    # An iterable of Requests to crawl from
    def start_requests(self):
        urls = [
            'https://link.springer.com/journals/{}/1'.format(chr(i+97)) for i in range(26)
        ]
        urls.append('https://link.springer.com/journals/0/1')
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    # Method to handle the response downloaded for each requests made
    def parse(self, response):
        # Redirect to journal information page
        info_links = response.xpath(
            '//main/ol/li[@class="c-atoz-list__item"]/a[@class="c-atoz-list__link"]/@href').getall()
        for info_link in info_links:
            journal_id = info_link.split('/')[-1]
            yield response.follow('https://www.springer.com/journal/{}'.format(journal_id), callback=self.parse_journal, method='GET')

        # Next page in list journal page
        next_page = response.xpath(
            '//main/div[@class="c-atoz-heading interface-bar"]//nav[@class="c-pagination-listed"]/ol/li/a[@rel="next"]/@href').get()
        logging.info('URL next_page: %s', next_page)
        if next_page != None:
            yield response.follow(next_page, self.parse)

    # Crawl metrics of journal
    def parse_journal(self, response):
        item = JournalMetric()
        logging.info('SplitURL: {}'.format(response.request.url.split("/")))

        journal_id_str = response.request.url.split("/")[-1]
        try:
            journal_id = int(journal_id_str)
            item['id'] = 'springer-{}'.format(journal_id)
        except ValueError:
            try:
                logging.info('SpecialURL: {}'.format(response.request.url))
                journal_id = int(response.request.url.split("/")[-2])
                item['id'] = 'springer-{}'.format(journal_id)
            except ValueError:
                pass

        item['title'] = response.xpath(
            '//header//div[@id="journalTitle"]/a/text()').get()
        item['editors'] = response.xpath(
            '//section[@class="app-section"]/dl[@class="c-list-description__item"]//li/text()').get()
        item['impact_factor'] = response.xpath(
            '//section[@class="app-journal-metrics"]/dl/dd[@data-test="impact-factor-value"]/text()').get()
        item['downloads'] = response.xpath(
            '//section[@class="app-journal-metrics"]/dl/dd[@data-test="metrics-downloads-value"]/text()').get()
        item['stfd'] = response.xpath(
            '//section[@class="app-journal-metrics"]/dl/dd[@data-test="metrics-speed-value"]/text()').get()
        item['fyif'] = response.xpath(
            '//section[@class="app-journal-metrics"]/dl/dd[@data-test="five-year-impact-factor-value"]/text()').get()
        item['sta'] = response.xpath(
            '//section[@class="app-journal-metrics"]/dl/dd[@data-test="metrics-acceptance-time-value"]/text()').get()

        yield item
