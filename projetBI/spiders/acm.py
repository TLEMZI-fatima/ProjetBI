import scrapy
import logging
from scrapy_splash import SplashRequest



class AcmSpider(scrapy.Spider):
    name = 'acm'
    allowed_domains = ['acm.org']

    def __init__(self, topic='', keywords='', **kwargs):
        super().__init__(**kwargs)
        self.start_urls = ['https://dl.acm.org/action/doSearch?AllField=%s' % keywords]
        self.topic = topic

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, callback=self.find_articles, args={'wait': 10})

    def find_articles(self, response):
        # logging.info(response.text)
        articles_urls = response.xpath('.//*/div[contains(@class,"issue-item")]/*/h5/span/a/@href').getall()
        logging.info(f'{len(articles_urls)} articles found')
        for url in articles_urls:
            article_url = 'https://dl.acm.org' + url
            yield SplashRequest(article_url, callback=self.parse, args={'wait': 10})

        next_page = response.xpath('.//*/nav[contains(@class, "pagination")]/span/a[@title="Next Page"]/@href').get(
            default='')
        logging.info('Next page found:')
        if next_page != '':
            yield SplashRequest(next_page, callback=self.find_articles, args={'wait': 10})

    def parse(self, response):
        logging.info('Processing --> ' + response.url)

        authors = response.xpath('//*/div[@class="citation"]/div/div/ul/li/a/@title').getall()
        result = {
            'title': response.xpath('//*/h1[@class="citation__title"]/text()').get(default=''),
            'authors': '|'.join(authors),
            # 'country': '',
            'abstract': response.xpath('//*/div[contains(@class,"abstractSection")]/p/text()').get(default=''),
            'date_pub': response.xpath('//*/span[@class="epub-section__date"]/text()').get(default=''),
            'journal': response.xpath('//*/span[@class="epub-section__title"]/text()').get(default=''),
            'topic': self.topic
            # 'latitude': '',
            # 'longitude': ''
        }
        yield result
