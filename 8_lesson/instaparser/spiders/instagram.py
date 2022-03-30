import scrapy
import json
import re
from scrapy.http import HtmlResponse
# from urllib.parse import urlencode
# from copy import deepcopy
from instaparser.items import InstaparserItem


class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['instagram.com']
    start_urls = ['https://www.instagram.com/']
    inst_login_link = 'https://www.instagram.com/accounts/login/ajax/'
    inst_login = 'Onliskill_udm'
    inst_passw = '#PWD_INSTAGRAM_BROWSER:10:1643131213:AZZQAGTPs6xfu+lt7ppOoFuIqKbWrZ4VaEX53g+SZCn8PJlFrepy7g4RoBJ9hG8g+yNb2R3TWGMrJek2u4SWHgpXYJPp7CijVJirea6j+tAGshfXR9HonVrpXtM9HF0oH+v2RlGNdeDqkBSgLuKb'
    user_for_pase = 'techskills_2022'

    def parse(self, response: HtmlResponse):
        csrf_token = self.fetch_csrf_token(response.text)

        yield scrapy.FormRequest(self.inst_login_link,
                                 method='POST',
                                 callback=self.login,
                                 formdata={'username': self.inst_login,
                                           'enc_password': self.inst_passw},
                                 headers={'X-CSRFToken': csrf_token})

    def login(self, response: HtmlResponse):
        j_body = response.json()
        if j_body['authenticated']:
            yield response.follow(f'/{self.user_for_pase}', callback=self.followers_parse, cb_kwargs={'username': self.user_for_pase})

    def followers_parse(self, response: HtmlResponse, username):
        user_id = self.fetch_user_id(response.text, username)
        url = f"https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count=12&search_surface=follow_list_page"
        yield response.follow(
            url,
            callback=self.followers_parse_next,
            headers={'User-Agent': 'Instagram 105.0.0.11.118'},
            cb_kwargs={'username': username,
                       'user_id': user_id})

    def followers_parse_next(self, response: HtmlResponse, username, user_id):
        j_data = response.json()
        max_id = j_data.get('next_max_id')
        if j_data['next_max_id']:
            url = f"https://i.instagram.com/api/v1/friendships/{user_id}/followers/?count=12&{max_id}&search_surface=follow_list_page"
            yield response.follow(url,
                                  callback=self.followers_parse_next,
                                  headers={'User-Agent': 'Instagram 105.0.0.11.118'},
                                  cb_kwargs={'username': username,
                                  'user_id': user_id})

        users = j_data.get('users')
        for user in users:
            item = InstaparserItem(
                user_name=user.get('Object').get('username'),
                user_id=user.get('Object').get('pk'),
                photo=user.get('Object').get('profile_image'),
                user_data=user.get('Object'))
            yield item

    def fetch_csrf_token(self, text):
        ''' Get csrf-token for auth '''
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

    def fetch_user_id(self, text, username):
        try:
            matched = re.search(
                '{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text
            ).group()
            return json.loads(matched).get('id')
        except:
            return re.findall('\"id\":\"\\d+\"', text)[-1].split('"')[-2]