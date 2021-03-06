# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class TestScrapyItem(Item):
    # Need id for check while upsert
    issn = Field()
    title = Field()
    impact_factor = Field()
    downloads = Field()
    stfd = Field()      # Submission to first decision - Time to first decision
    fyif = Field()
    sta = Field()
    # editors = Field()
