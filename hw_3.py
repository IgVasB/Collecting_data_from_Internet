import json
from bs4 import BeautifulSoup
import requests
import unicodedata
from pymongo import MongoClient
from hashlib import md5
from pymongo.errors import DuplicateKeyError
from pprint import pprint

url = 'https://hh.ru/search/vacancy'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.4896.75 Safari/537.36'}
vac = input('Какая позиция интересует? ')
max_pages = int(input('Сколько страниц смотреть? '))

def validate_data(data):
    if data:
        data = data.getText()
        data = unicodedata.normalize("NFKD", data)
    else:
        data = None
    return data

# Агрегация данных со страниц сайта (вывод по 20 позиций на страницу)
jobs_list = []
for page in range(max_pages):
        url_2 = f'{url}?page={page}&items_on_page=20&text={vac}'
        response = requests.get(url_2, headers=headers)
        dom = BeautifulSoup(response.text, 'html.parser')
        jobs = dom.find_all('div', {'class': 'vacancy-serp-item'})
        for job in jobs:
            job_data = {}
            job_title = validate_data(job.find("a", {"data-qa": "vacancy-serp__vacancy-title"}))
            job_employer = validate_data(job.find('div', {'class': 'vacancy-serp-item__meta-info-company'}))
#            job_link = job.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).get('href')
            job_link = job.find('a', {'data-qa': 'vacancy-serp__vacancy-title'})['href']
            job_salary = job.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
            job_salary_data = {'min_salary': 'None', 'max_salary': 'None', 'currency': 'None'}
            if job_salary: # если список не пуст
                job_salary = job_salary.text.replace("\u202f", '').split()
                job_salary_data['currency'] = job_salary[-1] # если не пусто, то валюта указана последней
                if 'от' in job_salary:
                    job_salary_data['min_salary'] = int(job_salary[1])
                if 'до' in job_salary:
                    job_salary_data['max_salary'] = int(job_salary[1])
                if '–' in job_salary:
                    job_salary_data['min_salary'] = int(job_salary[0])
                    job_salary_data['max_salary'] = int(job_salary[2])
            keyword = job_title + job_employer + job_link + str(job_salary_data)
            job_data['_id'] = md5(keyword.encode('utf-8')).hexdigest() # вычисляем хэш выражения - уникальный ID
            job_data['job_title'] = job_title
            job_data['job_employer'] = job_employer
            job_data['job_link'] = job_link
            job_data['min_salary'] = job_salary_data['min_salary']
            job_data['max_salary'] = job_salary_data['max_salary']
            job_data['currency'] = job_salary_data['currency']
            jobs_list.append(job_data)

print(f'Общее количество полученных вакансий: {len(jobs_list)}')
print(f'Вакансии сохранены в файле {vac}.json')

# Сохраняем в json файл
with open(f'{vac}.json', 'w', encoding='utf-8') as file:
    json.dump(jobs_list, file, ensure_ascii=False, indent=4)

client = MongoClient('127.0.0.1', 27017)
db = client['jobs_list']
for pos in jobs_list:
    try:
        db.vacancy.insert_one(pos)
    except DuplicateKeyError:
        print(f"Document with id = {pos['_id']} already exist")

min_req_salary = float(input('Вакансии с зарплатой (в рублях) не менее чем: '))
my_request = {'$and': [{'max_salary': {'$gte': min_req_salary}},
                       {'min_salary': {'$gte': min_req_salary}},
                       {'currency': 'руб.'}]}
my_request_jobs = list(db.vacancy.find(my_request))
pprint(my_request_jobs)