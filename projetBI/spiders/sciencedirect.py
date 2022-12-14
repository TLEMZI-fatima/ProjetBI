import scrapy
import logging
import re
from scrapy_splash import SplashRequest

from projetBI.items import ProjetbiItem


class SciencedirectSpider(scrapy.Spider):
    name = 'sciencedirect'
    allowed_domains = ['sciencedirect.com']
    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}

    def __init__(self, topic='', keywords='', **kwargs):
        super().__init__(**kwargs)
        self.start_urls = ['https://www.sciencedirect.com/search?qs=%s' % keywords]
        self.topic = topic

    def start_requests(self):
        for url in self.start_urls:
            yield SplashRequest(url, callback=self.find_articles, args={'wait': 4})

    def find_articles(self, response):
        logging.info(response.text)
        articles_urls = response.xpath('//*/div/h2/span/a/@href').getall()
        logging.info(f'{len(articles_urls)} articles found')
        for article_url in articles_urls:
            article_url = 'https://www.sciencedirect.com' + article_url
            yield SplashRequest(article_url, callback=self.parse_article, args={'wait': 4})

        next_page = response.xpath('//*[@id="srp-pagination"]/li[@class="pagination-link next-link"]/a/@href').get(
            default='')
        logging.info('Next page found:')
        if next_page != '':
            next_page = 'https://www.sciencedirect.com' + next_page
        yield SplashRequest(next_page, callback=self.find_articles)

    def parse_article(self, response):
        article = ProjetbiItem()
        logging.info('Processing --> ' + response.url)

        article.title = response.xpath('//*/article/h1/span').get(default='')
        authors = []
        authors_surnames = response.xpath('//*/div[@class="author-group"]/a/span/span[@class="text surname"]').getall()
        authors_givennames = response.xpath(
            '//*/div[@class="author-group"]/a/span/span[@class="text given-name"]').getall()
        for i in range(0, len(authors_givennames)):
            authors.append(authors_surnames[i] + ' ' + authors_givennames[i])
        article.authors = '|'.join(authors)
        article.country = ''
        article.abstract = response.xpath('//*/div[@class="abstract author"]/div/p').get(default='')
        article.date_pub = response.xpath('//*/div[@class="Publication"]/div/div').get(default='').split(',')[1]
        article.journal = response.xpath('//*/div[@class="Publication"]/div/h2').get(default='')
        article.topic = self.topic
        article.latitude = ''
        article.longitude = ''

        yield article
