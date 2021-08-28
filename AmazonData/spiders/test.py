import scrapy
from urllib.parse import urlencode
import re
import json
import os


API = os.getenv("Scraper_API")                    

def get_url(url):
    payload = {'api_key': API, 'url': url, 'country_code': 'us'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url


class LiteSpider(scrapy.Spider):
    name = 'test'
    start_urls=[get_url('https://www.amazon.com/dp/B01E17LNNU'),get_url('https://www.amazon.com/dp/B07BPG9YX9')]

    def parse(self, response):
        title = response.xpath(
            '//*[@id="productTitle"]/text()').extract_first()
        image = re.search('"large":"(.*?)"', response.text).groups()[0]
        rating = response.xpath('//*[@id="acrPopover"]/@title').extract_first()
        number_of_reviews = response.xpath(
            '//*[@id="acrCustomerReviewText"]/text()').extract_first()
        price = response.xpath(
            '//*[@id="priceblock_ourprice"]/text()').extract_first()
        category = response.xpath(
            '//a[@class="a-link-normal a-color-tertiary"]/text()').extract()[1].replace(' ', '').replace('\n', '').replace('&','and')
        if not price:
            price = response.xpath('//*[@data-asin-price]/@data-asin-price').extract_first(
            ) or response.xpath('//*[@id="price_inside_buybox"]/text()').extract_first()

        temp = response.xpath('//*[@id="twister"]')
        sizes = []
        colors = []
        if temp:
            s = re.search(
                '"variationValues" : ({.*})', response.text).groups()[0]
            json_acceptable = s.replace("'", "\"")
            di = json.loads(json_acceptable)
            sizes = di.get('size_name', [])
            colors = di.get('color_name', [])

        Description = response.xpath(
            '//*[@id="feature-bullets"]//li/span/text()').extract()
        seller_rank = response.xpath(
            '//*[text()="Amazon Best Sellers Rank:"]/parent::*//text()[not(parent::style)]').extract()
        yield {'asin': "1111", 'Title': title, 'MainImage': image, 'Rating': rating, 'NumberOfReviews': number_of_reviews,
               'Price': price, 'AvailableSizes': sizes, 'AvailableColors': colors, 'Description': Description,
               'SellerRank': seller_rank, 'category': category}

