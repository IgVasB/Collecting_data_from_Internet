# Вариант 2
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from pymongo import MongoClient
from pprint import pprint
import time

client = MongoClient('127.0.0.1', 27017)
db = client['mvideo']

s = Service('./chromedriver')
driver = webdriver.Chrome(service=s)

driver.get('https://www.mvideo.ru/')
driver.execute_script("window.scrollTo(0, 1700)")
time.sleep(5)

items = driver.find_elements(By.XPATH, "//mvid-product-cards-group/*")

goods_list = []
goods_info = {}

for item in items:
    if item.get_attribute('class') == 'product-mini-card__name ng-star-inserted':
        goods_info['name'] = item.find_element(By.XPATH, './div/a/div').text
        goods_info['link'] = item.find_element(By.XPATH, './/a').get_attribute('href')
    if item.get_attribute('class') == 'product-mini-card__price ng-star-inserted':
        goods_info['price'] = item.find_element(By.XPATH, ".//span[@class='price__main-value']").text
    if item.get_attribute('class') == 'product-mini-card__controls buttons ng-star-inserted':
        # пишем в базу данных Монго
        if db.goods.find_one({'link': goods_info['link']}):
            print(f'Duplicated product {goods_info["link"]}')
        else:
            db.goods.insert_one(goods_info)
        goods_list.append(goods_info)
        goods_info = {}
driver.quit()
pprint(goods_list)