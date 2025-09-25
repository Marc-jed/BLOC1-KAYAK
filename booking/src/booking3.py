from fileinput import filename
import scrapy
import json
from collections import defaultdict
import os
import logging
from scrapy.crawler import CrawlerProcess

class BookingSpider(scrapy.Spider):
    name = "booking"
    list1 = ['Paris', 'Bayeux']

    def __init__(self, *args, **kwargs):
        super(BookingSpider, self).__init__(*args, **kwargs)
        # Dictionnaire pour stocker les items par ville
        self.items_by_city = defaultdict(list)

    def start_requests(self):
        for city in self.list1:
            url = (
                f'https://www.booking.com/searchresults.fr.html?label=gog235jc-1DCAEoggI46AdIDVgDaE2IAQGYAQ24ARjIAQzYAQPoAQH4AQKIAgGoAgS4ArSp9L4GwAIB0gIkNWE0MGMxMDYtMGZiZC00NTVjLWJiYTUtZTJlZTk4YWY5ZDVi2AIE4AIB&sid=99a8fcc836ba77a8b3590c2fc844f80e&aid=397594&ss={city}&lang=fr&dest_id=-1456928&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=fr&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=54b476426b6107b9&group_adults=2&no_rooms=1&group_children=0&nflt=ht_id%3D204&order=bayesian_review_score'
            )
            
            yield scrapy.Request(url=url, callback=self.parse, meta={'city': city})

    def parse(self, response):
        city = response.meta['city']
        hotels = response.xpath('//div[contains(@data-testid, "property-card")]')

        for list_hotel in hotels:
            name = list_hotel.xpath('.//div[@data-testid="title"]/text()').get().strip()
            url = list_hotel.xpath('.//a[@data-testid="title-link"]/@href').get()
            rating = list_hotel.xpath('.//div[@data-testid="review-score"]/div/text()').get()

            if url:
                url = response.urljoin(url)
                yield response.follow(url, self.parse_hotel, meta={'name': name, 'rating': rating, 'city': city})
            else:
                self.logger.warning(f"Pas d'URL trouvée pour l'hôtel: {name}")

    def parse_hotel(self, response):
        name = response.meta['name']
        rating = response.meta['rating']
        city = response.meta['city']
        gps = response.xpath('//a[@id="map_trigger_header"]/@data-atlas-latlng').get()
        latitude, longitude = gps.split(',') if gps else (None, None)
        description = response.xpath('//p[@data-testid="property-description"]/text()').get()

        # Ajouter l'item au dictionnaire
        self.items_by_city[city].append({
            'name': name,
            'description': description,
            'url': response.url,
            'rating': rating,
            'latitude': latitude,
            'longitude': longitude
        })

    def closed(self, reason):
        # Enregistrer les items dans des fichiers séparés pour chaque ville
        for city, items in self.items_by_city.items():
            filename = f"results_{city.lower()}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(items, f, ensure_ascii=False, indent=4)

        if filename in os.listdir('booking/src/'):
                os.remove('booking/src/' + filename)  

    process = CrawlerProcess(settings = {
        'USER_AGENT': 'Chrome/97.0',
        'LOG_LEVEL': logging.INFO,
        "FEEDS": { 'booking/src/' +
            filename : {"format": "json"},
        }
    })