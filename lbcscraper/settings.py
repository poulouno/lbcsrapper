# -*- coding: utf-8 -*-

# Scrapy settings for lbcscraper project
#
# For simplicity, this file contains only the most important settings by
# default. All the other settings are documented here:
#
#     http://doc.scrapy.org/en/latest/topics/settings.html
#

BOT_NAME = 'lbcscraper'

SPIDER_MODULES = ['lbcscraper.spiders']
NEWSPIDER_MODULE = 'lbcscraper.spiders'

# Crawl responsibly by identifying yourself (and your website) on the user-agent
#USER_AGENT = 'lbcscraper (+http://www.yourdomain.com)'

# Obey robots.txt rules
ROBOTSTXT_OBEY = False

# Configure maximum concurrent requests performed by Scrapy (default: 16)
CONCURRENT_REQUESTS = 1

# Configure a delay for requests for the same website (default: 0)
# See http://scrapy.readthedocs.org/en/latest/topics/settings.html#download-delay
# See also autothrottle settings and docs
DOWNLOAD_DELAY = 0.1

#Configure item pipelines
# See http://scrapy.readthedocs.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {
    #'scrapyelasticsearch.scrapyelasticsearch.ElasticSearchPipeline': 500,
    'lbcscraper.pipelines.DuplicatesPipeline': 100,
    'lbcscraper.pipelines.durationPipeline': 200,
    'lbcscraper.pipelines.distancePipeline': 300,
}

# scrapyelasticsearch configuration
ELASTICSEARCH_SERVERS = ['localhost']
ELASTICSEARCH_INDEX = 'scrapy-lbc'
ELASTICSEARCH_TYPE = 'items'
ELASTICSEARCH_UNIQ_KEY = 'link'
ELASTICSEARCH_BUFFER_LENGTH = 10