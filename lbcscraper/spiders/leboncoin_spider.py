# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from datetime import datetime
import re
import scrapy
from urlparse import urlparse
from scrapy.contrib.spiders import CrawlSpider, Rule
from scrapy.contrib.linkextractors import LinkExtractor
from lbcscraper.items import LbcPropertyItem, LbcCarItem, LbcItem
import lbcscraper.MapsUtils as mu

from ElasticHelpers import ElasticHelpers


class LeboncoinSpider(CrawlSpider):
    name = "leboncoin"
    allowed_domains = ["leboncoin.fr"]
    

    def __init__(self, *args, **kwargs):
        """
        Retrieves start_urls from command line options:
        scrapy crawl leboncoin -a start_urls="http://www.leboncoin.fr/vetements/offres/languedoc_roussillon/herault/,http://www.leboncoin.fr/vetements/offres/languedoc_roussillon/herault/"
        """
        self.elastic = ElasticHelpers(self)
        self.rules = (
            # follows next pages but stop at 9 to avoid crawling for too long
            Rule(LinkExtractor(allow=r'.*?page=[1-9]?\&.*'), follow=True, callback='parse_items'),
            #Rule(LinkExtractor(allow=r'https:\/\/www\.leboncoin\.fr\/\w+\/\d+\.htm'),
            #     callback='parse_items', follow=True)
        )
        super(LeboncoinSpider, self).__init__(*args, **kwargs)
        start_urls = kwargs.get('start_urls')
        self.start_urls = start_urls and start_urls.split(',') or []
        self.LbcItemType = LbcItem

    def custom_start_requests(self):
        for url in self.start_urls:
            yield self.make_requests_from_url(url)

    def parse_start_url(self, response):
        return self.parse_items(response)

    @staticmethod
    def add_scheme_if_missing(url):
        """
        Adds the http:// scheme if missing in the URL.
        >>> url = 'www.leboncoin.fr/'
        >>> LeboncoinSpider.add_scheme_if_missing(url)
        'http://www.leboncoin.fr/'
        >>> url = '//www.leboncoin.fr/'
        >>> LeboncoinSpider.add_scheme_if_missing(url)
        'http://www.leboncoin.fr/'
        >>> url = 'http://www.leboncoin.fr/'
        >>> LeboncoinSpider.add_scheme_if_missing(url)
        'http://www.leboncoin.fr/'
        """
        parsed_url = urlparse(url)
        if not parsed_url.netloc:
            url = 'www.leboncoin.fr' + url
        if not parsed_url.scheme:
            # the '//' could or couldn't be omitted
            if not url.startswith('//'):
                url = '//' + url
            url = 'http:' + url
        return url

    def parse_items(self, response):
        print 'parsing'
        # selects the middle ads list, but not the right side ads
        #ads_elems = response.xpath('//section[contains(@class, "mainList")]//ul/li/a[contains(@class, "list_item")]')
        ads_elems = response.xpath("//*[@data-qa-id='aditem_container']")
        #aditem_container
        print ads_elems[0]
        for ad_elem in ads_elems:
            item = self.LbcItemType()
            links = ad_elem.xpath('a/@href').extract()
            print "\n"
            if not links:
                print("missing link")
                continue
            link = links[0]
            link = LeboncoinSpider.add_scheme_if_missing(link)
            print link
            item['link'] = link
            titles = ad_elem.xpath('a/@title').extract()
            
            titles_cleaned = [s.strip() for s in titles]
            print titles_cleaned[0]
            item['title'] = titles_cleaned[0]
            prices = ad_elem.xpath("*[@itemprop='price']").extract()
            print prices
            
            prices_cleaned = [float(s.replace(u"\xa0€", "").replace(" ", "").strip()) for s in prices]
            if prices_cleaned:
                item['price'] = prices_cleaned[0]
            photos = ad_elem.xpath('div[@class="item_image"]/span[@class="item_imagePic"]/span/@data-imgsrc').extract()
            if photos:
                photo = LeboncoinSpider.add_scheme_if_missing(photos[0])
                item['photo'] = photo
            request = scrapy.Request(link, callback=self.parse_item_details)
            request.meta['item'] = item
            print item
            yield request

    def parse_item_details(self, response):
        item = response.meta['item']
        #extract date
        date = response.xpath("//*[@data-qa-id='adview_date']/text()")[0].extract()
        print "date", date
        #remove that 'à'
        stdate = date.replace('à', '')
        datetime_object = datetime.strptime(stdate, '%d/%m/%Y %Hh%M')
        if date:
            item['date'] = str(datetime_object)

        cities = response.xpath("//*[@data-qa-id='adview_location_informations']/span/text()")[0].extract()
        
        if cities:
            item['city'] = cities
        postcodes = response.xpath("//*[@data-qa-id='adview_location_informations']/span/text()")[2].extract()
        if postcodes:
            item['postcode'] = postcodes
        #print cities, postcodes
        distance, duration =  mu.getDistance("meylan", "{}, {}".format(postcodes, cities))
        #print distance, duration 
        if distance:
            item['distance'] = distance
        if duration:
            item['duration'] = duration
        # yield item
        return item

class LeboncoinPropertySpider(LeboncoinSpider):
    """
    scrapy crawl leboncoin_property -a start_urls="http://www.leboncoin.fr/ventes_immobilieres/offres/languedoc_roussillon/herault/"
    """
    name = "leboncoin_property"

    def __init__(self, *args, **kwargs):
        """
        Overrides the Item type to a LbcPropertyItem.
        """
        super(LeboncoinPropertySpider, self).__init__(*args, **kwargs)
        self.LbcItemType = LbcPropertyItem

    def parse_item_details(self, response):
        item = super(LeboncoinPropertySpider, self).parse_item_details(response)
        surfaces_areas = response.xpath("//*[@data-qa-id='criteria_item_square']/div/div/text()").extract()[1]
        if surfaces_areas:
            item['surface_area'] = surfaces_areas
  
        return item


class LeboncoinCarSpider(LeboncoinSpider):
    """
    scrapy crawl leboncoin_car -a start_urls="https://www.leboncoin.fr/voitures/offres/languedoc_roussillon/?th=1&location=Montpellier%2034000&parrot=0"
    """
    name = "leboncoin_car"

    def __init__(self, *args, **kwargs):
        """
        Overrides the Item type to a LbcCarItem.
        """
        super(LeboncoinCarSpider, self).__init__(*args, **kwargs)
        self.LbcItemType = LbcCarItem

    def parse_item_details(self, response):
        item = super(LeboncoinCarSpider, self).parse_item_details(response)
        properties_elem = response.xpath('//section[contains(@class, "properties")]')
        # make
        makes = properties_elem.xpath('div/h2/span[contains(text(), "Marque")]/following-sibling::span/text()').extract()
        makes_cleaned = [s.replace(" ", "") for s in makes]
        if makes_cleaned:
            item['make'] = makes_cleaned[0]
        # model
        models = properties_elem.xpath('div/h2/span[contains(text(), "Modèle")]/following-sibling::span/text()').extract()
        models_cleaned = [s.replace(" ", "") for s in models]
        if models_cleaned:
            item['model'] = models_cleaned[0]
        # year
        years = properties_elem.xpath('div/h2/span[contains(text(), "Année-modèle")]/following-sibling::span/text()').extract()
        years_cleaned = [int(s.replace(" ", "").strip()) for s in years]
        if years_cleaned:
            item['year'] = years_cleaned[0]
        # mileage
        mileages = properties_elem.xpath('div/h2/span[contains(text(), "Kilométrage")]/following-sibling::span/text()').extract()
        mileages_cleaned = [int(s.lower().replace("km", "").replace(" ", "")) for s in mileages]
        if mileages_cleaned:
            item['mileage'] = mileages_cleaned[0]
        # fuel
        fuels = properties_elem.xpath('div/h2/span[contains(text(), "Carburant")]/following-sibling::span/text()').extract()
        fuels_cleaned = [s.replace(" ", "") for s in fuels]
        if fuels_cleaned:
            item['fuel'] = fuels_cleaned[0]
        # gearbox
        gearboxes = properties_elem.xpath('div/h2/span[contains(text(), "Boîte de vitesse")]/following-sibling::span/text()').extract()
        gearboxes_cleaned = [s.replace(" ", "") for s in gearboxes]
        if gearboxes_cleaned:
            item['gearbox'] = gearboxes_cleaned[0]
        return item
