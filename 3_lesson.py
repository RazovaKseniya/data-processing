from bs4 import BeautifulSoup as bs
import requests
import json
import re
from pprint import pprint
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError as dke

client = MongoClient('127.0.0.1', 27017)

db = client['jobs_hh']
vacancies_hh = db.vacancies_hh

def hh(job, n_str):
    jobs = []

    headers = {
        'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36'}
    base_url = 'https://hh.ru'
    url = 'https://hh.ru/search/vacancy?clusters=true&area=1&ored_clusters=true&enable_snippets=true&salary=&text=' + job
    i = 1

    while i <= n_str:
        response = requests.get(url, headers=headers)
        if response.ok:
            dom = bs(response.text, 'html.parser')
            jobs_block = dom.find_all('div',{'class':'vacancy-serp-item'})

            for job in jobs_block:
                job_data={}
                data = job.find('a',{'data-qa':'vacancy-serp__vacancy-title'})
                job_title = data.getText()
                link = data['href'].split('?')
                block_link = link[0]

                salary = job.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
                if not salary:
                    salary_min = None
                    salary_max = None
                    salary_in = None
                else:
                    salary = salary.getText().replace(u'\xa0', u'')
                    salary = re.split(r'\s|[-–, ]', salary)

                    if salary[0] == 'до':
                        salary_min = None
                        if salary[2] == '000':
                            salary_max = salary[1] + salary[2]
                            salary_max = int(salary_max)
                    elif salary[0] == 'от':
                        salary_max = None
                        if salary[2] == '000':
                            salary_min = salary[1] + salary[2]
                            salary_min = int(salary_min)
                    else:
                        salary_min = salary[1] + salary[2]
                        salary_min = int(salary_min)
                        salary_max = salary[3] + salary[4]
                        salary_max = int(salary_max)
                    salary_in = salary[-1]

                job_data['name'] = job_title
                job_data['salary_min'] = salary_min
                job_data['salary_max'] = salary_max
                job_data['salary_in'] = salary_in
                job_data['link'] = block_link

                vacancies_hh.update_one(job_data, {'$set': job_data}, upsert=True)

            page_text = dom.find('a', {'data-qa': 'pager-next'})
            if page_text:
                link_btn = page_text['href']
            else:
                break

        url = base_url + link_btn
        i = i + 1

    return jobs

vacancies = hh('Юрист', 2)

for job_data in vacancies_hh.find({}):
    print(job_data)

def wish_salary():
    salary = int(input('Enter salary: '))
    for job_data in vacancies_hh.find({'$or': [{'salary_min': {'$gte': salary}}, {'salary_max': {'$gte': salary}}]}):
        print(job_data)

wish_salary()

with open('hh_vacancies.json', 'w') as hvc:
    json.dump(vacancies, hvc)