# -*- coding: utf-8 -*-
#
# Содержит класс с логином к WikiAPI, методом записи текста на страницы, получения викикода страниц.
# И несколько функций вне кдасса:  page_get_html(title),  page_html_parsed(title) - получение html статей и парсинг для обработки
#
from commons import *

class wikiconnect:
	from constans import ask_save_prompts
	global URLapi, URLindex, URLhtml
	# URLapi = 'https://ru.wikipedia.org/w/api.php'
	# URLindex = 'https://ru.wikipedia.org/w/index.php'
	# URLhtml = 'https://ru.wikipedia.org/wiki/'
	# API_URL = 'https://ru.wikipedia.org/api/rest_v1/page/html/'  # cached_html, может быть старой
	# headers = {'user-agent': 'user:textworkerBot'}
	__username = ''
	__password = ''
	edit_token = ''
	edit_cookie = ''

	def __init__(self):
		with open('password.txt') as __f:  # , encoding='utf-8' 'ascii'
			self.__username = __f.readline().strip()
			self.__password = __f.readline().strip()
		self.login()

	def login(self):
		# Login request
		payload = {'action': 'query', 'format': 'json', 'utf8': '', 'meta': 'tokens', 'type': 'login'}
		r1 = requests.post(self.URLapi, data=payload)

		# login confirm
		login_token = r1.json()['query']['tokens']['logintoken']
		payload = {'action':     'login', 'format': 'json', 'utf8': '', 'lgname': self.__username,
				   'lgpassword': self.__password, 'lgtoken': login_token}
		r2 = requests.post(self.URLapi, data=payload, cookies=r1.cookies)

		# get edit token2
		params3 = '?format=json&action=query&meta=tokens&continue='
		r3 = requests.get(self.URLapi + params3, cookies=r2.cookies)
		edit_token = r3.json()['query']['tokens']['csrftoken']

		edit_cookie = r2.cookies.copy()
		edit_cookie.update(r3.cookies)

		self.edit_token = edit_token
		self.edit_cookie = edit_cookie


class wikiapi_works(wikiconnect):
	title = ''

	def __init__(self, title):
		super().__init__()
		self.title = title

	def get_wikicode(self):
		payload = {'action': 'raw', 'title': self.title}
		r4 = requests.post(self.URLindex, data=payload)
		if not r4.text:
			print(r4.text)
			input('Не получен текст страницы: {}'.format(self.title))
			return False
		else:
			return r4.text

	def save(self, text, mode='', summary = ''):
		# save action
		while True:
			parameters = {'action':       'edit', 'title': self.title, 'summary': summary,
					   'contentmodel': 'wikitext', 'format': 'json', 'utf8': '', 'bot': True,
					   'assert':       'user', 'token': self.edit_token}

			# Селектор: заменять текст, добавлять в начало, в конец
			if mode == 'appendtext':
				parameters['appendtext'] = text
			elif mode == 'prependtext':
				parameters['prependtext'] = text
			elif mode == 'undo':  # undo не подключено
				return
			else:
				parameters['text'] = text

			# Запрос подтверждения записи
			if self.ask_save_prompts:
				prompt = input('Записать замену текста {} на {}, введите "y" (yes) или "ya" (yes all)? ')
				# prompt = input('Записать замену текста {} на {}, введите "y" (yes) или "ya" (yes all)? '.format(replacetext_old,replacetext_new))
				if prompt not in ['y', 'ya']:
					return ''
				if prompt == 'ya':
					self.ask_save_prompts = False

			r4 = requests.post(self.URLapi, data=parameters, cookies=self.edit_cookie)

			if 'error' in r4.json():
				if r4.json()['error']['code'] == 'notoken':
					self.login()
				else:
					print(r4.text)
					return r4.text
			else:
				# if 'Success' not in r4.json()['edit']['result']:
				# print(r4.text)
				return r4.text

	def replace_text(self, replacetext_old, replacetext_new, summary=''):
		text = self.get_wikicode()  # text = get_wikicodet(title)
		if not text: return
		if text.find(replacetext_old):
			text = text.replace(replacetext_old, replacetext_new)
			result = self.save(text, 'replace', summary)
			print(result)

	def replace_text_regexp(self, regexp_compiled, replace, summary=''):
		page = self.get_wikicode()  # text = get_wikicodet(title)
		if not page_wikicode: return
		searched = regexp_compiled.search(page)
		if searched:
			print('replace_text')
			newtext = regexp_compiled.sub(replace, page)
			result = self.save(newtext, 'replace', summary)
			print(result)

	def add_text(self, text, mode, summary=''):
		# Селектор: заменять текст, добавлять в начало, в конец
		if mode not in ['appendtext', 'prependtext']:
			print('ошибка в параметре зароса add_text()')
		else:
			result = self.save(text, mode, summary)
			print(result)

	# def replace_or_add_text_regexp(self, regexp_compiled, replace, summary=''):  #add_br_before=True,
	# 	page = self.get_wikicode()  # text = get_wikicodet(title)
	# 	if not page: return
	# 	searched = regexp_compiled.search(page)
	# 	if searched:
	# 		if searched:
	#
	# 			print('replace_text')
	# 			newtext = regexp_compiled.sub(replace, page)
	# 			result = self.save(newtext, 'replace', summary)
	# 		else:
	# 			print('appendtext')
	# 			result = self.save(replace, 'appendtext', summary)
	# 		print(result)
	# 		print('ok')


def page_get_html(title):
	global PYTHON_VERSION, headers, URLhtml
	# title = self.title
	# data = {"title": title, "action": "render"}  # html
	payload = {"action": "render"}  # html
	if PYTHON_VERSION == 3:
		pageurl = URLhtml + quote(title)  # + '?action=render'  # python 3
	else:
		# title = pathname2url(title)  # python 2.7
		pageurl = URLhtml + title.encode('utf-8')  # + '?action=render'  # python 2.7
	# title = pathname2url(url)  # python 2.7
	# print(url)  # python 2.7
	# r = urlopen(url).read()  # cached_html  # urlopen берёт в byte-формате, request в str-формате
	## url = urlencode(url, data, quote_via=quote)
	# return r
	# ---
	# r = requests.get(API_URL, urlencode(data, quote_via=quote), headers=headers_)
	r = requests.get(pageurl, data=payload, headers=headers)  # cached_html
	return r.text


def page_html_parsed(title):
	from lxml import html
	p_html = page_get_html(title)
	p_html_parsed = html.fromstring(p_html)
	return p_html_parsed