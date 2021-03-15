import scrapy
import time
import unidecode
from crawl_journal.items import JournalMetric


class ElsevierSpider(scrapy.Spider):
    name = 'journal'
    allowed_domains = ['elsevier.com', 'springer.com', 'tandfonline.com', 'onlinelibrary.wiley.com']

    def start_requests(self):
        # SPRINGER
        urls_springer = [
            'https://link.springer.com/journals/{}/1'.format(chr(i+97)) for i in range(26)
        ]
        urls_springer.append('https://link.springer.com/journals/0/1')
        for url in urls_springer:
            yield scrapy.Request(url=url, callback=self.parse_springer)
        # ELSEVIER
        page = 138
        urls_elsevier = [
            'https://www.elsevier.com/catalog?producttype=journals&page={}'.format(i+1) for i in range(138)
        ]
        for url in urls_elsevier:
            yield scrapy.Request(url=url, callback=self.parse_elsevier)
        # TANDFONLINE
        urls_tandfonline = [
            'https://www.tandfonline.com/action/showPublications?pubType=journal&alphabetRange={}'.format(chr(i+97)) for i in range(26)
        ]
        for url in urls_tandfonline:
            yield scrapy.Request(url=url, callback=self.parse_tandfonline)
        # WILEY
        urls_wiley = [
            'https://onlinelibrary.wiley.com/action/showPublications?PubType=journal&alphabetRange={}'.format(chr(i+97)) for i in range(26)
        ]
        urls_wiley.append('https://onlinelibrary.wiley.com/action/showPublications?PubType=journal&alphabetRange=0-9')
        for url in urls_wiley:
            yield scrapy.Request(url=url, callback=self.parse_wiley)

    # --------------------------------------------------------------------------------------------------
    # ---------------------------------------------SPRINGER---------------------------------------------
    # --------------------------------------------------------------------------------------------------
    def parse_springer(self, response):
        info_links = response.xpath(
            '//main/ol/li[@class="c-atoz-list__item"]/a[@class="c-atoz-list__link"]/@href').getall()
        for info_link in info_links:
            journal_id = info_link.split('/')[-1]
            yield response.follow('https://www.springer.com/journal/{}'.format(journal_id), callback=self.parse_journal_springer)

        next_page = response.xpath(
            '//main/div[@class="c-atoz-heading interface-bar"]//nav[@class="c-pagination-listed"]/ol/li/a[@rel="next"]/@href').get()
        if next_page != None:
            yield response.follow(next_page, callback=self.parse_springer)

    def parse_journal_springer(self, response):
        item = JournalMetric()

        issn = response.xpath(
            '//div[contains(@class,"c-list-description__item")]/dd/text()'
        ).get()
        if issn != None:
            item['issn'] = issn.replace("-", "").strip()
        item['impact_factor'] = response.xpath(
            '//section[@class="app-journal-metrics"]/dl/dd[@data-test="impact-factor-value"]/text()').get()
        item['stfd'] = response.xpath(
            '//section[@class="app-journal-metrics"]/dl/dd[@data-test="metrics-speed-value"]/text()').get()
        item['fyif'] = response.xpath(
            '//section[@class="app-journal-metrics"]/dl/dd[@data-test="five-year-impact-factor-value"]/text()').get()
        item['sta'] = response.xpath(
            '//section[@class="app-journal-metrics"]/dl/dd[@data-test="metrics-acceptance-time-value"]/text()').get()
        # item['title'] = response.xpath(
        #     '//header//div[@id="journalTitle"]/a/text()').get()
        yield item

    # --------------------------------------------------------------------------------------------------
    # ---------------------------------------------ELSEVIER---------------------------------------------
    # --------------------------------------------------------------------------------------------------
    def parse_elsevier(self, response):
        info_links = response.xpath(
            '//div[@class="listing-product-links--inner"]/a/@href'
        ).getall()
        for info_link in info_links:
            yield response.follow(info_link, callback=self.parse_journal_elsevier)

    def parse_journal_elsevier(self, response):
        item = JournalMetric()

        issn = response.xpath(
            '//div[contains(@class, "issn")]/span/text()').get()
        if issn != None:
            item['issn'] = issn.replace("-", "").strip()
        item['fyif'] = response.xpath(
            '//div[@id="LeftCol1"]/div[@class="menu-item"]/div[1]/ul/li[text()[contains(., "5-Year Impact Factor")]]/span/b/text()').get()
        item['impact_factor'] = response.xpath(
            '//div[@id="Title"]//div[@class="publication"]//div[@class="publication-metrics"]//a[@aria-controls="publicationMetricTooltipImpactFactor"]/b/text()').get()
        item['stfd'] = response.xpath(
            '//div[@id="Title"]//div[@class="publication"]//div[@class="publication-metrics"]//a[@aria-controls="publicationMetricTooltipTtfdWeeks"]/b/text()').get()
        # item['title'] = response.xpath(
        #     '//div[@id="Title"]//h1[@itemprop="name"]/text()').get()
        yield item

    # --------------------------------------------------------------------------------------------------
    # -------------------------------------------TANDFONLINE--------------------------------------------
    # --------------------------------------------------------------------------------------------------
    def parse_tandfonline(self, response):
        info_links = response.xpath(
            '//a[@class="ref"]/@href').getall()
        for info_link in info_links:
            journal_code = info_link.split('/')[2]
            time.sleep(1)         
            yield response.follow('https://www.tandfonline.com/action/journalInformation?show=journalMetrics&journalCode={}'.format(journal_code), callback=self.parse_journal_tandfonline)

        next_page = response.xpath(
            '//a[@class="nextPage  js__ajaxSearchTrigger"]/@href').get()
        if next_page != None:
            time.sleep(1)
            yield response.follow(next_page, self.parse_tandfonline)

    def parse_journal_tandfonline(self, response):
        item = JournalMetric()

        title = response.xpath(
            '//span[@class="journal-heading"]/a/text()').get().strip()
        if title != None:
            item['title'] = unidecode.unidecode(title)
        item['impact_factor'] = response.xpath(
            '//div[@class="citation-metrics"]/ul/li[text()[contains(., "Impact Factor")]]/strong/text()').get()
        item['fyif'] = response.xpath(
            '//div[@class="citation-metrics"]/ul/li[text()[contains(., "5 year IF")]]/strong/text()').get()
        stfd = response.xpath(
            '//div[@class="speed"]/ul/li[text()[contains(., "from submission to first decision")]]/strong/text()').get()
        if stfd != None:
            item['stfd'] = stfd + ' days'
        return item

    # --------------------------------------------------------------------------------------------------
    # -----------------------------------------------WILEY----------------------------------------------
    # --------------------------------------------------------------------------------------------------
    def parse_wiley(self, response):
        info_links = response.xpath(
            '//ul[@class="rlist separator search-result__body titles-results"]/li//a[@class="visitable"]/@href').getall()
        for info_link in info_links:
            yield response.follow('https://onlinelibrary.wiley.com{}'.format(info_link), callback=self.parse_journal_wiley)

        next_page = response.xpath(
            '//a[@title="Next page"]/@href').get()
        if next_page != None:
            yield response.follow(next_page, self.parse_wiley)

    def parse_journal_wiley(self, response):
        item = JournalMetric()

        issn = response.xpath(
            '//div[contains(@class,"journal-info-container")]//span[contains(@class,"label") and contains(text(), "ISSN")]/../span[2]/text()').get()
        item['issn'] = issn.replace("-", "").strip()
        item['impact_factor'] = response.xpath(
            '//div[contains(@class,"journal-info-container")]//span[contains(@class,"label") and contains(text(), "Impact factor")]/../span[2]/text()').get()
        # item['title'] = response.xpath(
        #     '//meta[@property="og:title"]/@content').get()
        yield item