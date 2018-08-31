# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html


class LbcscraperPipeline(object):
    def process_item(self, item, spider):
        return item


from scrapy.exceptions import DropItem

class distancePipeline(object):

    max_distance = 60

    def process_item(self, item, spider):
        if item['distance'] <= self.max_distance:
            return item
        else:
            raise DropItem("distance is too long %s" % item)

class durationPipeline(object):

    max_duration = 45

    def process_item(self, item, spider):
        if item['duration'] <= self.max_duration:
            return item
        else:
            raise DropItem("duration is too long %s" % item)

class DuplicatesPipeline(object):

    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        if item['link'] in self.ids_seen:
            raise DropItem("Duplicate item found: %s" % item)
        else:
            self.ids_seen.add(item['link'])
            return item