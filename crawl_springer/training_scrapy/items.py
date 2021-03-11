# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field


class JournalMetric(Item):
    # Need id for check while upsert
    id = Field()
    title = Field()
    editors = Field()
    impact_factor = Field()
    downloads = Field()
    stfd = Field()          # Submission to first decision
    fyif = Field()
    sta = Field()          # Submission to acceptance
