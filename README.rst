scrapyrwiki
===========

A collection of helpers for running scrapers built with
`Scrapy <http://scrapy.org/>`_ in `ScraperWiki <https://scraperwiki.com/>`_


Launch scraper without scrapy CLI
---------------------------------

Example:

.. code:: python

    from scrapy.conf import settings
    from scrapyrwiki import run_spider

    def main():
        run_spider(MySpider(), settings)

    if __name__ == '__main__':
        main()


Save produced data to ScraperWiki
---------------------------------

Just add "scrapyrwiki.pipelines.ScraperWikiPipeline" to ITEM_PIPELINES

Example:

.. code:: python

    from scrapy.conf import settings
    from scrapyrwiki import run_spider

    def scraperwiki():
        options = {
            'SW_SAVE_BUFFER': 5,
            'SW_UNIQUE_KEYS': {"MyItem": ['url']},
            'ITEM_PIPELINES': ['scrapyrwiki.pipelines.ScraperWikiPipeline'],
        }
        settings.overrides.update(options)
        run_spider(MySpider(), settings)


    if __name__ == 'scraper':
        scraperwiki()


Check spider contracts in CI
----------------------------

Just launch spider with run_tests

Example:

.. code:: python

    from scrapyrwiki import run_tests
    from scrapy.conf import settings

    run_tests(MySpider(), "output.xml", settings)

Note: For testing the HTTP cache is used. In the directory where the script is
launched there must be a scrapy.cfg (needed by Scrapy to identify that's a scraper
directory) and a .scrapy directory with the HTTP cache db.

The output is in XUnit format, tested on `Jenkins <http://jenkins-ci.org>`_
