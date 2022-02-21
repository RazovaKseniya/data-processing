from bs4 import BeautifulSoup as bs
import requests
import json
import re
from pprint import pprint

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
                jobs.append(job_data)
            page_text = dom.find('a', {'data-qa': 'pager-next'})
            link_1 = page_text['href']
        url = base_url + link_1
        i = i + 1

    pprint(jobs)
    return jobs

vacancies = hh('Юрист', 2)

with open('hh_vacancies.json', 'w') as hvc:
    json.dump(vacancies, hvc)