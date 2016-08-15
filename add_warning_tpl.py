# -*- coding: utf-8  -*-#
# author: https://github.com/vladiscripts
#
# Добавление предупреждающего шаблона на страницы списка
# import wikiapi
import mwparserfromhell
from config import *
from wikiapi import page_get_html
from lib_for_mwparserfromhell import *


class Add_warning_tpl:

	def __init__(self, warning_tpl_name, pages_with_referrors):
		self.warning_tpl_name = warning_tpl_name
		self.page_text = "{{tpl_name | {{sub template}} some text}} text"

		for title in pages_with_referrors:
			self.page_err_refs = pages_with_referrors[title]
			self.do_page(title)


	def do_page(self, title):
		self.page_text = page_get_html(title)
		self.page_wikiparsed = mwparserfromhell.parse(self.page_text)


		self.update_page_tpl()

		self.page_text = str(self.page_wikiparsed)


		# # connect_properties = login_and_token(baseurl, username, password)
		# # r4_text = edit(baseurl, title, message, summary, connect_properties)
		# r4_text = edit(title, message, summary)
		# print(r4_text)
		# connect = wikiconnect()
		# if not connect
		#
		# for title in list_pages_with_referrors:
		# 	replacetext_old = '== Описание герба =='
		# 	refs_of_page = list_pages_with_referrors[title]
		# 	refs_str = '|'.join([refs_of_page.get(ref) for ref in refs_of_page])
		# 	replacetext_new = '\n' + '{{' + post_tpl_name + '|' + refs_str + '}}'
		#
		# 	page = wikiapi.wikiapi_works(title)
		# 	# page.replace_text_page(replacetext_old, replacetext_new, summary)
		# 	page.save_changed_text(replacetext_old, replacetext_new, summary)
		# 	del page
		# 	print(page)

	def change_with_regexp(self):
		regexp_compiled = re.compile(r'{{\s*' + warning_tpl_name + r'\s*(\|.*?)?}}', re.IGNORECASE)

		for title in pages_with_referrors:
			refs_of_page = pages_with_referrors[title]
			refs_str = '|'.join([refs_of_page.get(ref) for ref in refs_of_page])
			repl = '{{' + warning_tpl_name + '|' + refs_str + '}}'
			repl = '<code><nowiki>' + repl + '</nowiki></code>'  # обёртка в <nowiki>
			repl = '\n' + repl

			page = wikiapi.wikiapi_works(title)

			# page.replace_or_add_text_regexp(regexp_compiled, repl, summary)
			# def replace_or_add_text_regexp(self, regexp_compiled, replace, summary=''):  #add_br_before=True,

			page_wikicode = page.get_wikicode()
			if page:  # text = get_wikicodet(title)
				searched = repl.find(page_wikicode)  # проверка на наличие этого шабона с дубликатными refs
				if searched >= 0:
					print('уже есть в тексте')
					pass
				else:
					searched = regexp_compiled.search(page_wikicode)  # проверка на наличие шаблона вообще
					if searched:
						print('replace_text')
						newtext = regexp_compiled.sub(repl, page_wikicode)
						result = page.save(newtext, 'replace', summary)
					else:
						print('appendtext')
						result = page.save(repl, 'appendtext', summary)
					print(result)
					print('ok')

			# page_wikicode = page.get_wikicode()
			# searched = regexp_compiled.search(page_wikicode)
			# if searched:
			# 	_regexp
			# 	print('replace_text')
			# 	newtext_page = regexp_compiled.sub(repl, page_wikicode)
			# 	page.replace_text(page_wikicode, newtext_page, summary)
			# else:
			# 	print('appendtext')
			# 	page.add_text(repl, 'appendtext', summary)
			print('ok')


	def update_page_tpl(self):

		# parametersNamesList = parametersNamesList(tpl)

		# список значений параметров шаблона
		list_bad_sfn_links = set([ref['link_to_sfn'] for ref in self.page_err_refs])

		digits = re.compile(r'\d+')

		for template in self.page_wikiparsed.filter_templates():

			# Если предупреждающий шаблон уже есть на странице, то обновить его
			for tpl in self.page_wikiparsed.filter_templates():
				if tpl.name.matches(self.warning_tpl_name):

					for p in tpl.params:
						if digits.search(str(p.name).strip()):  # скан безымянных параметров
							# list_tpl_paramvalues.add(p.value.strip())
							wikilink = p.value.filter_wikilinks()  # викиссылки в параметрах
							if len(wikilink): wikilink = wikilink[0]
							# for wikilink in p.value.filter_wikilinks():  # викиссылки в параметрах
								wl = str(wikilink.title).strip()
								# убрать параметр, отсутствующий в списке ошибочных
								if wl not in list_bad_sfn_links:
									tpl.remove(p.name)






					# Если шаблон больше не нужен, то удалить его
					# wikicode.remove(tpl)
					# Удаление пустого шаблона (без параметров)
					for tpl in wikicode.filter_templates():
						if tpl.name.matches(tplname):
							for p in tpl.params:
								if digits.search(str(p.name).strip()):
									c = + 1
									if c == 0:
										wikicode.remove(tpl)
									# print('empty')
									# print(c)


				# Иначе добавить шаблон
				else:
					pass