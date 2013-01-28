from scrapy.crawler import CrawlerProcess
from scrapy import log


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
