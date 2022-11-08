import scrapy
import logging
import re
from scrapy_splash import SplashRequest

from projetBI.items import ProjetbiItem


class IeeeSpider(scrapy.Spider):
    name = 'ieee'
    allowed_domains = ['ieee.org']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
    #     "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8",
    #     "Accept-Language": "en-US,en;q=0.9",
    #     "Host": "www.adidas.com",
    #     "Connection": "keep-alive",
    #     "Upgrade-Insecure-Requests": "1",
    #      'CONCURRENT_REQUESTS': 10,
    # 'HTTPCACHE_ENABLED': True,
    # 'DOWNLOAD_DELAY': 5,
    # 'CONCURRENT_REQUESTS_PER_IP': 10,
    }

    def __init__(self, topic='', keywords='', **kwargs):
        super().__init__(**kwargs)
        self.start_urls = ['https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=%s' % keywords]
        self.topic = topic

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, callback=self.find_articles, args={'wait': 0.5,
             'viewport': '1024x2480',
             'timeout': 90,
             'images': 0,
             'resource_timeout': 10})

    def find_articles(self, response):
        logging.info(response.text)
        articles = response.xpath(
            '//*[@id="xplMainContent"]/div[2]/div[2]/xpl-results-list/div[3]/xpl-results-item/div[1]/div[1]/div[2]/h2/a').getall()
        logging.info(f'{len(articles)} articles found')
        for article_id in articles:
            article_id = re.findall("\d+", article_id)[-1]
            article_url = 'https://ieeexplore.ieee.org/document/' + \
                          str(article_id)
            yield SplashRequest(article_url, callback=self.parse, args={'wait': 2, 'viewport': '1024x2480',
             'timeout': 90,
             'images': 0})

        # finding and visiting next page
        ###

        ###next_page = response.xpath('//*[@class="w-button-more"]/a/@href').get(default='')
        ###logging.info('Next page found:')
        # if next_page != '':
        ###    next_page = 'https://mobile.twitter.com' + next_page
        # yield scrapy.Request(next_page, callback=self.find_tweets)
        ###

    def parse(self, response):
        article = ProjetbiItem()
        logging.info('Processing --> ' + response.url)

        article.title = ''
        article.authors = ''
        article.country = ''
        article.abstract = ''
        article.date_pub = ''
        article.journal = ''
        article.topic = self.topic
        article.latitude = ''
        article.longitude = ''

        yield article
