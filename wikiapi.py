# -*- coding: utf-8 -*-
#
# author: https://github.com/vladiscripts
#
# Содержит класс с логином к WikiAPI, методом записи текста на страницы, получения викикода страниц.
# И несколько функций вне кдасса:  page_get_html(title),  page_html_parsed(title) - получение html статей и парсинг для обработки
#
from sys import version_info
PYTHON_VERSION = version_info.major
if PYTHON_VERSION == 3:
	from urllib.parse import urlencode, quote  # python 3
else:
	from urllib import urlencode, quote  # python 2.7
	import codecs
import requests
from config import *


URLapi = 'https://ru.wikipedia.org/w/api.php'
URLindex = 'https://ru.wikipedia.org/w/index.php'
URLhtml = 'https://ru.wikipedia.org/wiki/'
headers = {'user-agent': 'user:textworkerBot'}
file_password_to_api = 'password.txt'  # 2 string: 1 - user, 2 -

# ---
ask_save_prompts = True  # работает с wikiAPI


class wikiconnect:
	def __init__(self):
		from config import ask_save_prompts
		global URLapi, URLindex, URLhtml
		self.URLapi = URLapi
		self.URLindex = URLindex
		self.URLhtml = URLhtml
		# URLapi = 'https://ru.wikipedia.org/w/api.php'
		# URLindex = 'https://ru.wikipedia.org/w/index.php'
		# URLhtml = 'https://ru.wikipedia.org/wiki/'
		# API_URL = 'https://ru.wikipedia.org/api/rest_v1/page/html/'  # cached_html, может быть старой
		# headers = {'user-agent': 'user:textworkerBot'}
		self.edit_token = ''
		self.edit_cookie = ''

		self.login()

	def login(self):
		global file_password_to_api
		with open(file_password_to_api) as __f:  # , encoding='utf-8' 'ascii'
			__username = __f.readline().strip()
			__password = __f.readline().strip()
		# Login request
		GETparameters = {'action': 'query', 'format': 'json', 'utf8': '', 'meta': 'tokens', 'type': 'login'}
		r1 = requests.post(self.URLapi, data=GETparameters)

		# login confirm
		login_token = r1.json()['query']['tokens']['logintoken']
		GETparameters = {'action':     'login', 'format': 'json', 'utf8': '', 'lgname': __username,
						 'lgpassword': __password, 'lgtoken': login_token}
		r2 = requests.post(self.URLapi, data=GETparameters, cookies=r1.cookies)

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
		GETparameters = {'action': 'raw', 'title': self.title}
		r4 = requests.post(self.URLindex, data=GETparameters)
		if not r4.text:
			print(r4.text)
			input('Не получен текст страницы: {}'.format(self.title))
			return False
		else:
			self.wikicode = r4.text
			return r4.text

	def save(self, text, mode='', summary=''):
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
		text = self.get_wikicode()
		if not text: return
		if text.find(replacetext_old):
			text = text.replace(replacetext_old, replacetext_new)
			result = self.save(text, 'replace', summary)
			print(result)

	def replace_text_regexp(self, regexp_compiled, replace, summary=''):
		text = self.get_wikicode()
		if not text: return
		searched = regexp_compiled.search(text)
		if searched:
			print('replace_text')
			newtext = regexp_compiled.sub(replace, text)
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


	# ALPHA VERSION   - not works
	def remove_tpl(self, tpl_name):
		import mwparserfromhell

		if not self.wikicode:
			self.get_wikicode()

		# for template in wikicode.filter_templates():
		# 	if template.name.matches(tpl_name) and findLink(template, link2remove):
		#
		# list_transcludes = file_readlines_in_set('list_uses_warningtpl.txt')
		# listpages_for_remove = list_transcludes - err_refs
		# remove_template(tpl_name, listpages_for_remove)

	def remove_tpl_from_pages(tpl_name, list_pages):
		for title in list_pages:
			title.remove_tpl(tpl_name)


# end class definition --------------


def page_get_html(title):
	global PYTHON_VERSION, headers, URLhtml
	# title = self.title
	# data = {"title": title, "action": "render"}  # html
	GETparameters = {"action": "render"}  # html
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
	r = requests.get(pageurl, data=GETparameters, headers=headers)  # cached_html
	return r.text


def page_html_parse(title):
	# from lxml import html
	from lxml import etree
	p_html = page_get_html(title)
	p_html_parsed = etree.HTML(p_html)
	# p_html_parsed = html.fromstring(p_html)
	return p_html_parsed


def get_list_transcludes_of_tpls(sfns_like_names):
	if isinstance(sfns_like_names, str):
		sfns_like_names = [sfns_like_names]
	list = set()
	for tpl in sfns_like_names:
		url = 'http://tools.wmflabs.org/ruwikisource/WDBquery_transcludes_template/?lang=ru&format=json&template=' + quote(
			tpl)
		# GETparameters = {"action": "render"}  # html
		GETparameters = {}
		r = requests.get(url, data=GETparameters)
		list = list.union(r.json())
	return list


# ---------

def movePagesToNewCategory(from_, to_, summary_):
	# command = "python movepages.my -noredirect"
	command = 'python c:\pwb\pwb.py movepages.my -pt:0 -noredirect -simulate'
	from_ = ' -from:"' + from_ + '"'
	to_ = ' -to:"' + to_ + '"'
	summary_ = ' -summary:"' + summary_ + '"'
	run = command + from_ + to_ + summary_
	os.system(run)


def renameCategory(from_, to_, summary_):
	# command = "python category.py move"
	command = 'python c:\pwb\pwb.py category.py move -pt:0 -inplace -simulate'  # -keepsortkey
	from_ = ' -from:"' + from_ + '"'
	to_ = ' -to:"' + to_ + '"'
	summary_ = ' -summary:"' + summary_ + '"'
	run = command + from_ + to_ + summary_
