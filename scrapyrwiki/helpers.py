import os

from scrapy.crawler import CrawlerProcess
from scrapy import log


def run_spider(spider, settings, loglevel='INFO'):
    """
    Run a spider with given settings
    """
    if 'SENTRY_DSN' in os.environ:
        import scrapy_sentry
        scrapy_sentry.init(os.environ['SENTRY_DSN'])
        settings.overrides.update({
            'SENTRY_SIGNALS': ['spider_error']
        })
    crawler = CrawlerProcess(settings)
    crawler.install()
    crawler.configure()
    crawler.crawl(spider)
    log.start(loglevel=loglevel)
    crawler.start()
