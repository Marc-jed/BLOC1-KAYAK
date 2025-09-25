import os
import logging
import scrapy
from scrapy.crawler import CrawlerProcess

class BOOKINGspider(scrapy.Spider):
    # Name of your spider
    name = "Booking"

    # Url to start your spider from 
    start_urls =["https://www.booking.com/searchresults.fr.html?label=gog235jc-1DCAEoggI46AdIDVgDaE2IAQGYAQ24ARjIAQzYAQPoAQH4AQKIAgGoAgS4Auay774GwAIB0gIkNGE3ZDk4ZmYtODdhOC00OGM5LThlOWUtOGQzZTljNWU0NDBh2AIE4AIB&sid=ec59e03e7f5c5c4f9c4776cff5813f5c&aid=397594&ss=france&ssne=France&ssne_untouched=France&efdco=1&lang=fr&src=searchresults&dest_id=73&dest_type=country&ac_position=0&ac_click_type=b&ac_langcode=fr&ac_suggestion_list_length=5&search_selected=true&search_pageview_id=2b227334a2b50349&checkin=2025-05-05&checkout=2025-05-10&ltfd=5%3A1%3A4-2025%3A1%3A&group_adults=2&no_rooms=1&group_children=0&nflt=ht_id%3D204%3Breview_score%3D90",]

    def parse(self, response):
        return {
            'hotel': response.xpath("/html/body/div[4]/div/div/div/div[2]/div[3]/div[2]/div[4]/div[3]/div[4]/div[1]/div[2]/div/div[1]/div[1]/div/div[1]/div/h3/a/div[1]/text()").get(),  
        }

# Name of the file where the results will be saved
filename = "test_booking.json"

# If file already exists, delete it before crawling (because Scrapy will 
# concatenate the last and new results otherwise)
if filename in os.listdir('/content/drive/MyDrive/Colab Notebooks/Data Full Stack/Visual Code/Python/KAYAK/booking/src'):
        os.remove('/content/drive/MyDrive/Colab Notebooks/Data Full Stack/Visual Code/Python/KAYAK/booking/src' + filename)
     

process = CrawlerProcess(settings = {
    'USER_AGENT': 'Chrome/97.0',
    'LOG_LEVEL': logging.INFO,
    "FEEDS": {
        '/content/drive/MyDrive/Colab Notebooks/Data Full Stack/Visual Code/Python/KAYAK/booking/src' + filename : {"format": "json"},
    }
})

# Start the crawling using the spider you defined above
process.crawl(BOOKINGspider)
process.start()