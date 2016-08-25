# -*- coding: utf-8  -*-#
# author: https://github.com/vladiscripts
#
# Добавление предупреждающего шаблона на страницы списка
# import wikiapi
import re
import mwparserfromhell
from config import *
import wikiapi

# from lib_for_mwparserfromhell import *

# Обрабатывать только одну страницу, беря контент из файла. Например, для работы из бота AWB.
# do_only_1_page_by_content_from_file = True  # работает с вики-парсером
# filename_page_wikicontent = r'../temp/AWBfile.txt'  # страница в вики-разметке



class Add_warning_tpl:
	def __init__(self, warning_tpl_name, pages_with_referrors):
		global do_only_1_page_by_content_from_file, filename_page_wikicontent
		self.warning_tpl_name = warning_tpl_name
		# self.page_text = "{{tpl_name | {{sub template}} some text}} text"
		self.digits = re.compile(r'\d+')
		self.empty_str = re.compile(r'^\s*$')
		self.pages_with_referrors = pages_with_referrors

		if do_only_1_page_by_content_from_file:
			import sys
			if len(sys.argv) > 1:
				title = sys.argv[1].replace(' ', '_')
				try:
					self.page_err_refs = self.pages_with_referrors[title]
				except KeyError:
					print("This page no in error list.")  # Статьи нет в списке ошибочных
				else:
					self.page_wikitext = file_readtext(filename_page_wikicontent)
					self.do_page(title)
					file_savetext(filename_page_wikicontent, self.page_wikitext_final)
			else:
				print("Не указано название статьи параметром командной строки.")

		else:
			for title in self.pages_with_referrors:
				self.page = wikiapi.wikiapi_works(title)
				self.page_wikitext = self.page.get_wikicode()

				self.do_page(title)

			print("Запись страниц пока отключена.")
		# self.save_page()
		# self.page_wikitext_final = str(self.page_wikiparsed)

	def do_page(self, title):
		self.page_wikiparsed = mwparserfromhell.parse(self.page_wikitext)
		self.update_page_tpl()
		self.page_wikitext_final = str(self.page_wikiparsed)
		pass

	# def run(self):
	# 	for title in pages_with_referrors:
	# 		self.do_page(title)

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

	def add_tpl_if_no(self):
		# Добавить шаблон если нет на странице
		is_on_page = False
		for tpl in self.page_wikiparsed.filter_templates():
			if tpl.name.matches(self.warning_tpl_name):
				is_on_page = True
				break
		if not is_on_page:
			tpl = mwparserfromhell.nodes.template.Template(self.warning_tpl_name)
			self.page_wikiparsed.append("\n" + str(tpl))

	def delete_tpl_doubles(self):
		# удаление шаблонов-дублей
		is_first_found = 0
		for tpl in self.page_wikiparsed.filter_templates():
			if tpl.name.matches(self.warning_tpl_name):
				is_first_found += 1
				if is_first_found > 1:
					self.page_wikiparsed.remove(tpl)

	def delete_params_empty_and_is_not_1_wikilinks(self):
		# удаление пустых безымянных параметров и которые не 1 викиссылка
		p_trash = []
		for tpl in self.page_wikiparsed.filter_templates():
			if tpl.name.matches(self.warning_tpl_name):
				for p in tpl.params:
					if self.digits.search(str(p.name).strip()):  # скан безымянных параметров
						leng = len(p.value.filter_wikilinks())
						if self.empty_str.match(str(p.value)) or leng != 1:
							p_trash.append(p)
				for pt in p_trash:
					tpl.remove(pt)

	def update_page_tpl(self):

		# список значений параметров шаблона
		# list_bad_sfn_links = []
		# for ref in self.page_err_refs:
		# 	print(ref)
		# 	link_to_sfn = ref['link_to_sfn']
		# 	list_bad_sfn_links.append([ref['link_to_sfn'], ref['text']])
		list_bad_sfn_links = [[ref['link_to_sfn'], ref['text']] for ref in self.page_err_refs]

		# Добавить шаблон если нет на странице
		self.add_tpl_if_no()
		# self.page_wikiparsed = mwparserfromhell.parse(self.page_text)  # репарсинг, ибо добавление шаблона сбивает паршеный текст

		# удаление шаблонов-дублей
		self.delete_tpl_doubles()

		# удаление пустых безымянных параметров и без викиссылок
		self.delete_params_empty_and_is_not_1_wikilinks()

		# self.page_wikiparsed = mwparserfromhell.parse(self.page_text)  # репарсинг, ибо добавление шаблона сбивает паршеный текст


		# Если предупреждающий шаблон уже есть на странице, то обновить его
		# Чистка от параметров отсутствующих в актуальном списке ошибок
		for tpl in self.page_wikiparsed.filter_templates():
			if tpl.name.matches(self.warning_tpl_name):
				p_count_numeric = 0  # счётчик нумерованных (безымянных) параметрв в шаблоне
				tpl_numeric_params = []

				for p in tpl.params:
					if self.digits.search(str(p.name).strip()):  # скан безымянных параметров

						p_count_numeric += 1

						# list_tpl_paramvalues.add(p.value.strip())
						wikilinks = p.value.filter_wikilinks()  # викиссылки в параметрах
						# обрабатывать только первую викиссылу в параметре (на случай если кто-то вручную засунет туда лищних)
						# if len(wikilinks) == 0:

						if len(wikilinks) > 0:
							wikilink = wikilinks[0]
							# for wikilink in p.value.filter_wikilinks():  # викиссылки в параметрах
							# wl = set([str(wikilink.title).strip()
							# wl_text = str(wikilink.text).strip()

							wl = [str(wikilink.title).strip(), str(wikilink.text).strip()]
							# tpl_numeric_params.append(wl)

							# убрать параметр, отсутствующий в списке ошибочных
							if wl not in list_bad_sfn_links:
								tpl.remove(p.name)

							else:
								tpl_numeric_params.append(wl)

		# добавление параметров
		for tpl in self.page_wikiparsed.filter_templates():
			if tpl.name.matches(self.warning_tpl_name):
				# for p in tpl.params:
				# 	if self.digits.search(str(p.name).strip()):  # скан безымянных параметров
				for main_bad_ref in list_bad_sfn_links:
					# if main_bad_ref not in tpl_numeric_params:
					tpl_list_params = [p.value.strip() for p in tpl.params]
					main_bad_ref = r"[[#{link}|{text}]]".format(link=main_bad_ref[0], text=main_bad_ref[1])
					if main_bad_ref not in tpl_list_params:
						# find_free_num_for_paramname
						n = 1
						while tpl.has(n):
							n += 1
						tpl.add(n, main_bad_ref)
					# tpl.add(n, r"[[{link}|{text}]]\n".format(link=main_bad_ref[0], text=main_bad_ref[1]))

				# Удаление пустого шаблона без параметров - т.е. все проблемы ссылок были решены
				if len(tpl.params) == 0:
					self.page_wikiparsed.remove(tpl)


			# Иначе добавить шаблон
			else:
				pass

		# print(str(self.page_wikiparsed))
		pass

	#
	# def remove_tpl_from_changed_pages(tplname, list_with_err):
	# 	global pages_with_referrors
	# 	list_transcludes = file_readlines_in_set('list_uses_warningtpl.txt')
	# 	list_with_err = set([title for title in pages_with_referrors])
	# 	listpages_for_remove = list_transcludes - list_with_err
	# 	remove_tpl_from_pages(tplname, listpages_for_remove)

# test
#
# pages_with_referrors = {
# 	"Участник:Vladis13/статья": [
# 		{"link_to_sfn": "cite_note-2",
# 		 "ref":         "CITEREF1_sfn_.D1.81.D0.BD.D0.BE.D1.81.D0.BA.D0.B0",
# 		 "text":        "1 sfn сноска"
# 		 },
# 		{"link_to_sfn": "cite_note-2",
# 		 "ref":         "CITEREF2_sfn_.D1.81.D0.BD.D0.BE.D1.81.D0.BA.D0.B0",
# 		 "text":        "2 sfn сноска"
# 		 }
# 	]
# }

# pages_with_referrors = json_data_from_file(filename_listpages_errref_json)
# test = Add_warning_tpl(name_of_warning_tpl, pages_with_referrors)
