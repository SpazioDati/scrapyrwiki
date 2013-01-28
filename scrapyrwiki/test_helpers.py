from scrapy.xlib.pydispatch import dispatcher
from scrapy.crawler import CrawlerProcess
from scrapy import signals, log

from scrapy.commands.check import Command as CheckCommand
from scrapy.contracts import ContractsManager
from scrapy.utils.misc import load_object
from scrapy.utils.conf import build_component_list

from nose.plugins.xunit import Xunit
from nose.config import Config


class AttributeDict(dict):
    __getattr__ = dict.__getitem__


def run_tests(spider, output_file, settings):
    """
    Helper for running test contractors for a spider and output an
    XUnit file (for CI)

    For using offline input the HTTP cache is enabled
    """

    settings.overrides.update({
        "HTTPCACHE_ENABLED": True,
        "HTTPCACHE_EXPIRATION_SECS": 0,
    })

    crawler = CrawlerProcess(settings)

    contracts = build_component_list(
        crawler.settings['SPIDER_CONTRACTS_BASE'],
        crawler.settings['SPIDER_CONTRACTS'],
    )

    xunit = Xunit()
    xunit.enabled = True
    xunit.configure(AttributeDict(xunit_file=output_file), Config())
    xunit.stopTest = lambda *x: None

    check = CheckCommand()
    check.set_crawler(crawler)
    check.settings = settings
    check.conman = ContractsManager([load_object(c) for c in contracts])
    check.results = xunit
    # this are specially crafted requests that run tests as callbacks
    requests = check.get_requests(spider)

    crawler.install()
    crawler.configure()
    crawler.crawl(spider, requests)
    log.start(loglevel='DEBUG')

    # report is called when the crawler finishes, it creates the XUnit file
    report = lambda: check.results.report(check.results.error_report_file)
    dispatcher.connect(report, signals.engine_stopped)

    crawler.start()
