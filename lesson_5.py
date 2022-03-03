from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import time
from pymongo import MongoClient
from pprint import pprint

client = MongoClient('localhost', 27017)
db = client['mail_letters']
mail_letters = db.mail_letters

chrome_options = Options()
chrome_options.add_argument('start-maximized')

s = Service('./chromedriver.exe')
driver = webdriver.Chrome(service=s, options=chrome_options)

driver.get('https://account.mail.ru/login?page=https%3A%2F%2Fe.mail.ru%2Finbox%3Futm_source%3Dportal%26utm_medium%3Dmailbox%26utm_campaign%3De.mail.ru%26mt_click_id%3Dmt-veoz41-1646241779-2637336342&allow_external=1&from=octavius')

login = 'study.ai_172@mail.ru'
password = 'NextPassword172#'

wait = WebDriverWait(driver, 10)
elem = wait.until(EC.presence_of_element_located((By.NAME, "username")))
elem.send_keys(login)
elem.send_keys(Keys.ENTER)

elem = wait.until(EC.presence_of_element_located((By.NAME, "password")))
time.sleep(1)
elem.send_keys(password)
elem.send_keys(Keys.ENTER)
time.sleep(5)

links_list = []
for i in range(5):
    letters = driver.find_elements(By.XPATH, "//div[contains(@class, 'ReactVirtualized__Grid__innerScrollContainer')]/a")
    for letter in letters:
        if letter in links_list:
            pass
        else:
            links_list.append(letter.get_attribute('href'))
    actions = ActionChains(driver)
    actions.move_to_element(letters[-1])
    actions.perform()
    time.sleep(4)

time.sleep(2)
letters = driver.find_elements(By.CLASS_NAME, 'js-letter-list-item')

letters_list = []
for letter in letters:
    letter_data = {}
    letter_data['Sender'] = letter.find_element(By.CLASS_NAME,'ll-crpt').get_attribute('title')
    letter_data['Date'] = letter.find_element(By.XPATH, ".//div[contains(@class, 'llc__item llc__item_date')]").text
    letter_data['Title'] = letter.find_element(By.CLASS_NAME,'ll-sj__normal').text
    letter_data['Text'] = letter.find_element(By.CLASS_NAME,'ll-sp__normal').text
    letter_data['Link'] = letter.get_attribute('href')
    letters_list.append(letter_data)
    mail_letters.update_one(letter_data, {'$set': letter_data}, upsert=True)

for letter_data in mail_letters.find({}):
    print(letter_data)