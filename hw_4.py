# собираем новости с передовицы lenta.ru
import requests
import datetime
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from lxml import html
from pprint import pprint
from hashlib import md5

client = MongoClient('127.0.0.1', 27017)
db = client['news_from_lenta_ru']

url = 'https://lenta.ru'
headers = {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                         'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}
response = requests.get(url, headers=headers)
dom = html.fromstring(response.text)

news_list = []
main_news = dom.xpath('//div[@class="topnews__first-topic"]')[0]
news_all = dom.xpath("//a[@class='card-mini _topnews']")
news_all.append(main_news)
for news in news_all:
    news_lenta = {}
    if news.xpath(".//a/@class"):
        link = main_news.xpath(".//a/@href")[0]
        title = main_news.xpath(".//h3/text()")[0]
        time = main_news.xpath(".//time[@class='card-big__date']/text()")[0]
    else:
        link = news.xpath("./@href")[0]
        title = news.xpath(".//span[@class='card-mini__title']/text()")[0]
        time = news.xpath(".//time[@class='card-mini__date']/text()")[0]

    if link[0] == '/':
        link = url + link
    if len(time) <= 5:
        time = str(datetime.datetime.today().strftime('%Y-%m-%d ')) + time

    news_lenta['link'] = link
    news_lenta['title'] = title
    news_lenta['time'] = time
    news_lenta['site'] = 'Lenta.ru'
    news_lenta['_id'] = md5(str(news_lenta).encode('utf-8')).hexdigest()
    news_list.append(news_lenta)

    try:
         db.lenta_news.insert_one(news_lenta)
    except DuplicateKeyError:
         print(f"Document  {news_lenta['title']} already exist")

pprint(news_list)