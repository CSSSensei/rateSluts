import requests
import re
import os
from dotenv import load_dotenv, find_dotenv
import time
import datetime
load_dotenv(find_dotenv())

vk_token = os.getenv('VKTOKEN')
version = 5.92

def get_posts(parameters: dict) -> dict:
    photo_list = []
    flag = True
    offset = 0
    while len(photo_list) < parameters.get('photo_amount', 5) and flag:
        response = requests.get('https://api.vk.com/method/wall.get',
                                params={'access_token': vk_token,
                                        'v': version,
                                        'domain': parameters['domain'],
                                        'offset': offset * 100,
                                        'count': 100}
                                )
        time.sleep(0.25)
        offset += 1
        data = response.json()
        now = datetime.datetime.now()
        if int(parameters['time_delta']) == 0:
            day1 = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute) - datetime.timedelta(days=1)
            day2 = datetime.datetime(now.year, now.month, now.day, now.hour, now.minute)
        else:
            day1 = datetime.datetime(now.year, now.month, now.day, 23, 59) - datetime.timedelta(
                days=1 + int(parameters['time_delta']))
            day2 = datetime.datetime(now.year, now.month, now.day, 23, 59, 0) - datetime.timedelta(
                days=int(parameters['time_delta']))
        unix_time_day1 = int(day1.timestamp())
        unix_time_day2 = int(day2.timestamp())
        cnt = 0
        if len(data.get('response', {}).get('items',[])) > 0:
            data = data['response']['items']
        else:
            return {}
        for post in data:
            if post['date'] < unix_time_day1 and not post.get('is_pinned', False):
                flag = False
                break
            if not post.get('marked_as_ads', False) and not post.get('is_pinned', False) and post.get(
                    'attachments') and unix_time_day1 <= post['date'] and post['date'] <= unix_time_day2 and post['date'] >= parameters['last_update']:
                photo_exist = False
                for attachment in post['attachments']:
                    if attachment.get('type') == 'photo':
                        photo_exist = True
                        break
                if not photo_exist:
                    continue
                photo_list.append((post['attachments'], post.get('likes',{}).get('count', 0), post['text'], f"{post['from_id']}_{post['id']}"))
                if not parameters['top_likes']:
                    cnt += 1
                    if cnt >= parameters['photo_amount']:
                        break
    result = {}
    if not parameters['top_likes']:
        for post in photo_list:
            result[post[3]] = []
            for attachment in post[0]:
                if attachment.get('type') != 'photo':
                    continue
                max_size = 0
                url = ''
                for photo in attachment['photo']['sizes']:
                    if photo['width'] >= max_size:
                        url = photo['url']
                        max_size = photo['width']
                if url:
                    result[post[3]].append(url)
            result[post[3]] = (result[post[3]], post[2], post[1])
        return result

    photo_list_sorted = sorted(photo_list, key=lambda x: x[1], reverse=True)[:parameters['photo_amount']]
    for post in photo_list_sorted:
        result[post[3]] = []
        for attachment in post[0]:
            if attachment.get('type') != 'photo':
                continue
            max_size = 0
            url = ''
            for photo in attachment['photo']['sizes']:
                if photo['width'] >= max_size:
                    url = photo['url']
                    max_size = photo['width']
            if url:
                result[post[3]].append(url)
        result[post[3]] = (result[post[3]], post[2], post[1])
    return result


def api_group_name(domain):
    response = requests.get('https://api.vk.com/method/groups.getById',
                            params={'access_token': vk_token,
                                    'v': version,
                                    'group_id': domain}
                            )
    data = response.json()
    name = data['response'][0]['name']
    photo = data['response'][0]['photo_200']
    return name.replace('<','').replace('>',''), photo


def check_valid_url(url: str):
    if not re.match(r'^vk\.com\/.*$', url):
        if not re.match(r'^https:\/\/vk\.com\/.*$', url):
            if not re.match(r'^http:\/\/vk\.com\/.*$', url):
                return False,
    match = re.search(r'(?<=vk\.com\/).*$', url)
    if not match:
        return False,
    domain = match.group(0)

    response = requests.get('https://api.vk.com/method/wall.get',
                            params={'access_token': vk_token,
                                    'v': version,
                                    'domain': domain,
                                    'count': 1}
                            )
    data = response.json()
    if data.get('error') == None:
        return True, domain
    return False,


def format_text(text, domain, id):
    n_max = 700
    text = text.replace('<3', '❤️').replace('<', '').replace('>', '')
    if len(text) > n_max:
        text = text[:n_max] + f'...\n<i><a href="vk.com/{domain}?w=wall{id}">Читать далее</a></i>'
    return text
