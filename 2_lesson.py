from bs4 import BeautifulSoup as bs
import requests
import json
import pandas as pd
from pprint import pprint
import time

headers = {'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.80 Safari/537.36'}

def hh(main_link, search_str, n_str):
    html = requests.get(main_link + '/search/vacancy?clusters=true&enable_snippets=true&text=' + search_str + '&showClusters=true', headers = headers).text
    parsed_html = bs(html,'lxml')

    jobs = []
    for i in range(n_str):
        jobs_block = parsed_html.find('div',{'class':'vacancy-serp-item'})
        jobs_list = jobs_block.findChildren(recursive=False)
        for job in jobs_list:
            job_data={}
            req=job.find('span',{'class':'get-user-content'})
            if req!=None:
                main_info = req.findChild()
                job_name = main_info.getText()
                job_link = main_info['href']
                salary = job.find('span',{'data-qa':'vacancy-serp__vacancy-compensation'})
                if not salary:
                    salary_min=0
                    salary_max=0
                else:
                    salary=salary.getText().replace(u'\xa0', u' ')
                    salaries=salary.split('-')
                    salary_min=salaries[0]
                    if len(salaries)>1:
                        salary_max=salaries[1]
                    else:
                        salary_max=''
                job_data['name'] = job_name
                job_data['salary_min'] = salary_min
                job_data['salary_max'] = salary_max
                job_data['link'] = job_link
                job_data['site'] = main_link
                jobs.append(job_data)
        time.sleep(1)
        next_btn_block = parsed_html.find('a', {'class': 'bloko-button'})
        next_btn_link = next_btn_block['href']
        html = requests.get(main_link + next_btn_link, headers=headers).text
        parsed_html = bs(html, 'lxml')
    pprint(jobs)
    return jobs

vacancies = hh('https://hh.ru', 'Python', 4)

with open('hh_vacancies.json', 'w') as hvc:
    json.dump(vacancies, hvc)