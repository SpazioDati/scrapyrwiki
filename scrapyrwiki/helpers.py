from collections import defaultdict

from scrapy.xlib.pydispatch import dispatcher
from scrapy.crawler import CrawlerProcess
from scrapy import signals, log


class ScraperWikiPipeline(object):
    """
    A pipeline for saving to the Scraperwiki datastore

    If the scraper returns different kind of items they are stored in
    different tables
    """
    def __init__(self):
        self.buff = 20
        self.data = defaultdict(list)
        self.counter = 0
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def process_item(self, item, spider):
        item_type = item.__class__.__name__
        self.data[item_type].append(dict(item))
        if len(self.data[item_type]) >= self.buff:
            self.write_data(spider, item_type)
        return item

    def spider_closed(self, spider):
        for item_type in self.data:
            if self.data[item_type]:
                self.write_data(spider, item_type)

    def write_data(self, spider, item_type):
        import scraperwiki

        unique_keys = spider.settings.get(
            'SW_UNIQUE_KEYS', {item_type: ['id']}
        )
        scraperwiki.sqlite.save(
            table_name="%s_%s" % (spider.name, item_type),
            unique_keys=unique_keys,
            data=self.data[item_type]
        )
        self.data[item_type] = []


def run_spider(spider, settings, loglevel='INFO'):
    """
    Run a spider with given settings
    """
    crawler = CrawlerProcess(settings)
    crawler.install()
    crawler.configure()
    crawler.crawl(spider)
    log.start(loglevel=loglevel)
    crawler.start()
