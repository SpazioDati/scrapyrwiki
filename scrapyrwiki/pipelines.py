from collections import defaultdict

from scrapy.xlib.pydispatch import dispatcher
from scrapy import signals
from scraperwiki import sqlite
from datetime import datetime

import logging

def gen_table_name(item_type):
    table_name = item_type.lower()
    if table_name.endswith("item") and len(table_name) > 4:
        table_name = table_name[:-4]
    return table_name


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
        table_name = gen_table_name(item_type)
        unique_keys = spider.settings.get(
            'SW_UNIQUE_KEYS', {item_type: ['id']}
        )
        sqlite.save(
            table_name=table_name,
            unique_keys=unique_keys[item_type],
            data=self.data[item_type]
        )
        self.data[item_type] = []

class CreatedModifiedPipeline(ScraperWikiPipeline):
    """
    This pipeline extends ScraperWikiPipeline adding a created and a modified
    field to every item. These fields are updated according to the following
    rules:

     - If the item is not in the database both created and modified fields
    are set to datetime.utcnow()

     - If the item is alredy in the database and each and every field matches
    with that item's field then created and modified will not be changed

     - If the item is already in the database but one or more fields are
    different then updated will be set to datetime.utcnow(), while created
    will not be changed

    The test scraper for this pipeline can be found at:
    sw.spaziodati.eu/scrapers/test_created_modified_pipeline/
    """

    def update_item(self, item, item_type, unique_keys, table_name):
    	now = datetime.utcnow()
        where = ' and '.join([("%s = '%s'" % (ukey, item[ukey]))
            for ukey in unique_keys[item_type]])
        sqlquery = "* from %s where %s" % (table_name, where)
        
        try:
            item_in_database = sqlite.select(sqlquery)
            saved_item = { key: value
                for key, value in item_in_database[0].iteritems()
                if value and key not in ['created', 'modified'] 
            } # because the item to be saved doesn't have these fields

            current_item = { key: value
                for key, value in item.iteritems()
                if value
            } # ignoring blank/Nones etc.

            item['modified'] = (item_in_database[0]['modified']
                if current_item == saved_item and item_in_database[0]['modified']
                else now)

            item['created'] = (item_in_database[0]['created']
                if item_in_database[0]['created']
                else now)

        except (sqlite.SqliteError, IndexError, KeyError):
            item['created'] = item['modified'] = now

        return item

    def write_data(self, spider, item_type):
        table_name = gen_table_name(item_type)
        unique_keys = spider.settings.get(
            'SW_UNIQUE_KEYS', {item_type: ['id']}
        )

        updated = []
        for item in self.data[item_type]:
            try:
                updated_item =  self.update_item(item, item_type, unique_keys, table_name)
                updated.append(updated_item)
            except Exception as ex: 
                logging.exception('Pipeline error processing item %s' % str(item))

        self.data[item_type] = updated
        super(CreatedModifiedPipeline, self).write_data(spider, item_type)
