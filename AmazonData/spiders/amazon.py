import scrapy
from urllib.parse import urlencode
#from urllib.parse import urljoin
import os

queries = ['Cpu','jacket']
API = os.getenv("Scraper_API")


def get_url(url):
    payload = {'api_key': API, 'url': url, 'country_code': 'us'}
    proxy_url = 'http://api.scraperapi.com/?' + urlencode(payload)
    return proxy_url


class AmazonSpider(scrapy.Spider):
    name = 'amazon'

    def start_requests(self):
        for query in queries:
            url = 'https://www.amazon.com/s?' + urlencode({'k': query})
            yield scrapy.Request(url=get_url(url), callback=self.parse_keyword_response)

    def parse_keyword_response(self, response):
        products = response.xpath('//*[@data-asin]')
        for product in products:
            asin = product.xpath('@data-asin').extract_first()
            product_url = f"https://www.amazon.com/dp/{asin}"
            yield scrapy.Request(url=get_url(product_url), callback=self.parse_product_page, meta={'asin': asin})

        #next_page = response.xpath('//li[@class="a-last"]/a/@href').extract_first()
        # if next_page:
        #     url = urljoin("https://www.amazon.com",next_page)
        #     yield scrapy.Request(url=get_url(url), callback=self.parse_keyword_response)

    def parse_product_page(self, response):
        asin = response.meta['asin']
        title = response.xpath(
            '//*[@id="productTitle"]/text()').extract_first()
        image = response.xpath(
            "//img[@class='a-dynamic-image']/@src").extract_first()
        rating = response.xpath('//*[@id="acrPopover"]/@title').extract_first()
        number_of_reviews = response.xpath(
            '//*[@id="acrCustomerReviewText"]/text()').extract_first()
        price = response.xpath(
            '//*[@id="priceblock_ourprice"]/text()').extract_first()
        category = response.xpath(
            '//a[@class="a-link-normal a-color-tertiary"]/text()').extract()[1].replace(' ', '').replace('\n', '').replace('&', 'and')
        if not price:
            price = response.xpath('//*[@data-asin-price]/@data-asin-price').extract_first(
            ) or response.xpath('//*[@id="price_inside_buybox"]/text()').extract_first()


        Description = response.xpath(
            '//*[@id="feature-bullets"]//li/span/text()').extract()
        seller_rank = response.xpath(
            '//*[text()="Amazon Best Sellers Rank:"]/parent::*//text()[not(parent::style)]').extract()
      
        yield {'asin': asin, 'Title': title, 'MainImage': image, 'Rating': rating, 'NumberOfReviews': number_of_reviews,
               'Price': price, 'Description': Description,'SellerRank': seller_rank, 'category': category}
