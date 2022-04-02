import json
from bs4 import BeautifulSoup
import requests

url = 'https://hh.ru/search/vacancy'
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 \
        (KHTML, like Gecko) Chrome/100.0.4896.60 Safari/537.36'}
vac = input('Какая позиция интересует? ')
max_pages = int(input('Сколько страниц смотреть? '))

# Агрегация данных со страниц сайта (вывод по 20 позиций на страницу)
jobs_list = []
for page in range(max_pages):
        url_2 = f'{url}?page={page}&items_on_page=20&text={vac}'
        response = requests.get(url_2, headers=headers)
        dom = BeautifulSoup(response.text, 'html.parser')
        jobs = dom.find_all('div', {'class': 'vacancy-serp-item'})
        for job in jobs:
            job_data = {}
            job_title = job.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).text.strip()
            job_employer = job.find('div', {'class': 'vacancy-serp-item__meta-info-company'}).text.strip()
            job_link = job.find('a', {'data-qa': 'vacancy-serp__vacancy-title'}).get('href')
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
            job_data['job_title'] = job_title
            job_data['job_employer'] = job_employer
            job_data['job_link'] = job_link
            job_data['job_salary'] = job_salary_data
            jobs_list.append(job_data)

print(f'Общее количество полученных вакансий: {len(jobs_list)}')
print(f'Вакансии сохранены в файле {vac}.json')

# Сохраняем в json файл
with open(f'{vac}.json', 'w', encoding='utf-8') as file:
    json.dump(jobs_list, file, ensure_ascii=False, indent=4)