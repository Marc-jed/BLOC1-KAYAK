import os
import logging
import scrapy
from scrapy.crawler import CrawlerProcess


class BookingSpider(scrapy.Spider):
    name = "booking"

    start_urls = [
        'https://www.booking.com/searchresults.fr.html?label=gog235jc-1DCAEoggI46AdIDVgDaE2IAQGYAQ24ARjIAQzYAQPoAQH4AQKIAgGoAgS4ArSp9L4GwAIB0gIkNWE0MGMxMDYtMGZiZC00NTVjLWJiYTUtZTJlZTk4YWY5ZDVi2AIE4AIB&aid=397594&ss=Paris%2C+%C3%8Ele-de-France%2C+France&ssne=France&ssne_untouched=France&efdco=1&lang=fr&sb=1&src_elem=sb&dest_id=-1456928&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=fr&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=483d72d65e3101b2&group_adults=2&no_rooms=1&group_children=0&order=bayesian_review_score'
    ] 

    def parse(self, response):
        # Set pour garder une trace des hôtels déjà vus
        seen_hotels = set()

        hotels = response.xpath('//div[contains(@data-testid, "property-card")]')

        for list_hotel in hotels:
            name = list_hotel.xpath('.//div[@data-testid="title"]/text()').get().strip()
            url = list_hotel.xpath('.//a[@data-testid="title-link"]/@href').get()
            rating = list_hotel.xpath('.//div[@data-testid="review-score"]/div/text()').get()

            if url:
                url = response.urljoin(url)
                yield response.follow(url, self.parse_hotel, meta={'name': name, 'rating': rating})    
            else:
                self.logger.warning(f"Pas d'URL trouvée pour l'hôtel: {name}")
               
    def parse_hotel(self, response) :
        name = response.meta['name']   
        rating = response.meta['rating']
        # description = response.xpath('/html/body/div[4]/div/div[4]/div[1]/div[1]/div[2]/div/div[1]/div[1]/div[1]/div/div/p[1]/text()').get()
        gps = response.xpath('//a[@id="map_trigger_header"]/@data-atlas-latlng').get()
        latitude, longitude = gps.split(',') if gps else (None, None)
        description = response.xpath('//p[@data-testid="property-description"]/text()').get()
        yield {
            'name':name,
            'description':description,
            'url': response.url,
            'rating': rating,
            'latitude':latitude,
            'longitude':longitude
         }
         
# Name of the file where the results will be saved
filename = "test_booking3.json"

if filename in os.listdir('booking/src/'):
        os.remove('booking/src/' + filename)  

process = CrawlerProcess(settings = {
    'USER_AGENT': 'Chrome/97.0',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": { 'booking/src/' +
        filename : {"format": "json"},
    }
})







# Start the crawling using the spider you defined above
process.crawl(BookingSpider)
process.start()