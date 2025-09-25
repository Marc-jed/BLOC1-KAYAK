import os
import logging
import scrapy
from scrapy.crawler import CrawlerProcess


class BookingSpider(scrapy.Spider):
  
      name = "booking"
      city = ["Toulouse"]
    
      start_urls = [
        'https://www.booking.com/searchresults.fr.html?label=gog235jc-1DCAEoggI46AdIDVgDaE2IAQGYAQ24ARjIAQzYAQPoAQH4AQKIAgGoAgS4ArSp9L4GwAIB0gIkNWE0MGMxMDYtMGZiZC00NTVjLWJiYTUtZTJlZTk4YWY5ZDVi2AIE4AIB&aid=397594&ss=Paris%2C+%C3%8Ele-de-France%2C+France&ssne=France&ssne_untouched=France&efdco=1&lang=fr&sb=1&src_elem=sb&dest_id=-1456928&dest_type=city&ac_position=0&ac_click_type=b&ac_langcode=fr&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=483d72d65e3101b2&group_adults=2&no_rooms=1&group_children=0&order=bayesian_review_score'
      ] 
      def adresse_vers_gps(self,adresse):
        geolocator = Nominatim(user_agent="scrapy_bot")
        location = geolocator.geocode(adresse)
        if location:
          return location.latitude, location.longitude
        return None, None
      
      def parse(self, response):
        # Set pour garder une trace des hôtels déjà vus
        seen_hotels = set()
        hotels = response.xpath('//div[contains(@data-testid, "property-card")]')
      
        for hotel in hotels:
            name = hotel.xpath('.//div[@data-testid="title"]/text()').get()
            url = hotel.xpath('.//a[@data-testid="title-link"]/@href').get()
            # rating = hotel.xpath('.//div[@data-testid="review-score"]/div[1]/div/text()').get()
            rating = hotel.xpath('.//div[@data-testid="review-score"]/div/text()').get()
            description = hotel.xpath('.//div[@data-testid="property-card-description"]/text()').get()
            adresse = hotel.xpath('.//span[@data-testid="address"]/text()').get()  
    
            latitude, longitude = self.adresse_vers_gps(adresse) if adresse else (None, None)

            # Coordonnées GPS (présentes sous forme de dataset)
            # latitude = hotel.xpath('.//@data-lat').get()
            # longitude = hotel.xpath('.//@data-lng').get()

            yield {
                'hotel': name,
                'url': response.urljoin(url) if url else None,
                'rating': rating.strip() if rating else "Pas de note",
                'description': description.strip() if description else "Pas de description",
                'adresse' : adresse,
                'latitude': latitude,
                'longitude': longitude
            }

# Name of the file where the results will be saved
filename = "test_booking2.json"

if filename in os.listdir('booking/src'):
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