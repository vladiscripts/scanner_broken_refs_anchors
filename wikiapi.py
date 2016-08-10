# -*- coding: utf-8 -*-
# PYTHON_VERSION = 3  # для версии 2 отключить эту строку или сменить
# if PYTHON_VERSION == 3:
# 	from urllib.parse import urlencode, quote  # python 3
# else:
# 	from urllib import urlencode, quote  # python 2.7
# 	import codecs
# from constans import PYTHON_VERSION, urlencode, quote
from constans import *

class wikiconnect:
	from wikibot_password import username, password
	URLapi = 'https://ru.wikipedia.org/w/api.php'
	URLhtml = 'https://ru.wikipedia.org/wiki/'
	# API_URL = 'https://ru.wikipedia.org/api/rest_v1/page/html/'  # cached_html, может быть старой
	headers = {'user-agent': 'user:textworkerBot'}
	edit_token = ''
	edit_cookie = ''
	ask_save_prompts = True

	def __init__(self):
		self.login()

	def login(self):
		# Login request
		payload = {'action': 'query', 'format': 'json', 'utf8': '', 'meta': 'tokens', 'type': 'login'}
		r1 = requests.post(self.URLapi, data=payload)

		# login confirm
		login_token = r1.json()['query']['tokens']['logintoken']
		payload = {'action':     'login', 'format': 'json', 'utf8': '', 'lgname': self.username,
				   'lgpassword': self.password, 'lgtoken': login_token}
		r2 = requests.post(self.URLapi, data=payload, cookies=r1.cookies)

		# get edit token2
		params3 = '?format=json&action=query&meta=tokens&continue='
		r3 = requests.get(self.URLapi + params3, cookies=r2.cookies)
		edit_token = r3.json()['query']['tokens']['csrftoken']

		edit_cookie = r2.cookies.copy()
		edit_cookie.update(r3.cookies)

		# connect_properties = {'edit_token': self.edit_token, 'edit_cookie': self.edit_cookie}
		self.edit_token = edit_token
		self.edit_cookie = edit_cookie


class wikiapi_works(wikiconnect):
	title = ''

	def __init__(self, title):
		super().__init__()
		self.title = title

	def get_wikicode(self):
		baseurl = 'https://ru.wikipedia.org/w/index.php'
		payload = {'action': 'raw', 'title': self.title}
		r4 = requests.post(baseurl, data=payload)
		return r4.text

	def get_html(self):
		global PYTHON_VERSION
		# title = self.title
		# data = {"title": title, "action": "render"}  # html
		payload = {"action": "render"}  # html
		if PYTHON_VERSION == 3:
			url = self.URLhtml + quote(self.title)  # + '?action=render'  # python 3
		else:
			# title = pathname2url(title)  # python 2.7
			url = self.URLhtml + self.title.encode('utf-8')  # + '?action=render'  # python 2.7
		# title = pathname2url(url)  # python 2.7
		# print(url)  # python 2.7
		# r = urlopen(url).read()  # cached_html  # urlopen берёт в byte-формате, request в str-формате
		## url = urlencode(url, data, quote_via=quote)
		# return r
		# ---
		# r = requests.get(API_URL, urlencode(data, quote_via=quote), headers=headers_)
		r = requests.get(url, data=payload, headers=self.headers)  # cached_html
		return r.text


def save(self, text, summary, mode=''):
	# global baseurl, connect_properties
	# save action
	while True:
		payload = {'action':       'edit', 'title': self.title, 'summary': summary,
				   'contentmodel': 'wikitext', 'format': 'json', 'utf8': '', 'bot': True,
				   'assert':       'user', 'token': connect.edit_token}

		# Селектор: заменять текст, добавлять в начало, в конец
		if mode == 'appendtext':
			payload['payload'] = text
		elif mode == 'prependtext':
			payload['prependtext'] = text
		else:
			payload['text'] = text

		# Запрос подтверждения записи
		if connect.ask_save_prompts:
			prompt = input('Записать замену текста {} на {}, введите "y" (yes) или "ya" (yes all)? '.format(
					replacetext_old,
					replacetext_new))
			if prompt not in ['y', 'ya']:
				return
			if prompt == 'ya':
				connect.ask_save_prompts = False

		# r4 = requests.post(baseurl, data=payload, cookies=connect_properties['edit_cookie'])
		r4 = requests.post(connect.baseurl, data=payload, cookies=connect.edit_cookie)

		if 'error' in r4.json():
			if r4.json()['error']['code'] == 'notoken':
				connect.login()  # connect_properties = dict(edit_token='', edit_cookie='')
			else:
				print(r4.text)
				return r4.text
		else:
			# if 'Success' not in r4.json()['edit']['result']:
			# print(r4.text)
			return r4.text


def replace_text_page(self, replacetext_old, replacetext_new, summary):
	text = self.get_wikicode()  # text = get_wikicodet(title)
	if not text:
		input('Не получен текст страницы.')
	if text.find(replacetext_old):
		text = text.replace(replacetext_old, replacetext_new)
		result = self.save(text, summary)
		print(result)
