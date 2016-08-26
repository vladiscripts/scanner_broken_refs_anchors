# coding: utf8
#
# author: https://github.com/vladiscripts
#
from urllib.parse import quote
from config import *
import vladi_commons


class ScanRefsOfPage:
	def __init__(self, title, pages_count_cur):
		from wikiapi import page_html_parse, page_get_html
		self.list_sfns = set()
		self.list_refs = set()
		self.all_sfn_info_of_page = []
		self.full_errrefs = []

		self.title = title
		self.pages_count_cur = pages_count_cur
		self.parsed_html = page_html_parse(self.title)  # html из url
		self.find_sfns_on_page()
		self.find_refs_on_page()
		self.compare_refs()

	def find_sfns_on_page(self):
		try:
			p_ref_list = self.parsed_html.xpath("//ol[@class='references']/li")
			for li in p_ref_list:
				span_list = li.xpath("./span[@class='reference-text']")
				for span in span_list:
					a_list = span.xpath("./descendant::a[contains(@href,'CITEREF')]")
					for a in a_list:
						href = ''
						text = ''
						link_to_sfn = ''
						href = a.attrib['href']  # href = span.xpath("*/a[contains(@href,'CITEREF')]/@href")
						text = a.text
						link_to_sfn = li.attrib['id']  # li.xpath("./@id")

						href_cut = self.cut_href(a.attrib['href'])
						self.list_sfns.add(href_cut)
						self.all_sfn_info_of_page.append(
								{'citeref': href_cut, 'text': a.text, 'link_to_sfn': str(li.attrib['id'])})
						# self.ref_calls[href_cut] = {'text': a.text, 'link_to_sfn': str(li.attrib['id'])}
						pass

					# from lxml import cssselect
					# # for li in parsed_html.cssselect('li[href*="CITEREF"]'):
					# for eref in self.parsed_html.cssselect('span.reference-text a[href*="CITEREF"]'):
					# 	href = eref.get('href')
					# 	pos = href.find('CITEREF')
					# 	if pos >= 0:
					# 		href_cut = href[pos:]
					# 		self.list_sfns.add(href_cut)
					# 		# link_to_sfn ссылка на sfn-сноску
					# 		# print(href)
					# 		try:
					# 			link_to_sfn = self.parsed_html.xpath(
					# 					"//li[@id]/span/a[@href='{href}']/ancestor::li[contains(@id,'{link_to_sfn}')][1]/@id".format(
					# 							href=href, link_to_sfn='cite_note'))[0]
					# 		except IndexError:
					# 			try:
					# 				link_to_sfn = self.parsed_html.xpath(
					# 						"//li[@id]/span/cite/a[@href='{href}']/ancestor::li[contains(@id,'{link_to_sfn}')][1]/@id".format(
					# 								href=href, link_to_sfn='cite_note'))[0]
					# 			except IndexError:
					# 				link_to_sfn = '#Примечания'
					#
					# 		self.ref_calls[href_cut] = {'text': eref.text, 'link_to_sfn': str(link_to_sfn)}

		except Exception as error:
			self.error_print(error)

		# Отлов красных ошибок как в ст.  "Казаки" не получается
		# for undefined_ref in parsed_html.cssselect('li span.mw-ext-cite-error'):
		# for undefined_ref in parsed_html.cssselect('span.error'):
		# for undefined_ref in parsed_html.cssselect('span').text:
		# t = [undefined_ref for undefined_ref in parsed_html.xpath('//li[@id=cite_note-sol5_2_3-35]')]
		# t = parsed_html.cssselect('li')
		# t = [undefined_ref for undefined_ref in parsed_html.cssselect('li#cite_note-sol5_2_3-35')]
		# t = [undefined_ref for undefined_ref in parsed_html.xpath('//span/text')]
		# for undefined_ref in parsed_html.xpath('//span').text:
		# if 'Ошибка в сносках' in undefined_ref.text

	def cut_href(self, href):
		pos = href.find('CITEREF')
		if pos >= 0:
			return href[pos:]
		return False

	def find_refs_on_page(self):
		try:
			for xpath in ['//span[@class="citation"]/@id', '//cite/@id']:
				for href in self.parsed_html.xpath(xpath):
					self.list_refs.add(self.cut_href(href))

		except Exception as error:
			self.error_print(error)

	def compare_refs(self):
		# список сносок с битыми ссылками, из сравнения списков сносок и примечаний
		err_refs = self.list_sfns - self.list_refs
		# Если в статье есть некорректные сноски без целевых примечаний
		if err_refs:
			self.full_errrefs = []
			for citeref in sorted(err_refs):
				it_sfn_double = False
				for sfn in self.all_sfn_info_of_page:
					if sfn['citeref'] == citeref and not it_sfn_double:
						self.full_errrefs.append(sfn)
						it_sfn_double = True

			global print_log_full
			if print_log_full:
				print('Page # {}: {}'.format(self.pages_count_cur, self.title))
				# print(u'Ошибочные сноски типа sfn без связи с ref: {}'.format(self.list_pages_with_referrors[self.title]))
				print('Errorious sfn-like links without anchors in refs: {}'.format(self.full_errrefs))

	def find_refs_via_wikiparser(self, tpl):
		"""
		Поиск сносок по викикоду. Вместо него использован поиск по html-тэгу "CITEREF".
		Из-за вроде как лучшей скорости, совметимости с версией python на Tool labs,
		и обнаруженных нюансов, что шаблоны используются по разному.
		(Например, якоря ставятся не параметром "|ref=" шаблонов,
		а отдельными шаблонами якоей, или ручными вставками html-кода.)
		У "CITEREF" тоже есть нюансы, но вроде пороще.
		@return:
		"""
		list_tpls = set()
		list_refs = set()
		list_sfns = set()

		if tpl.has('ref'):
			refs = [tpl.get('ref').value.strip()]
			for year in [u'год', 'year']:
				if tpl.has(year):
					refs.append(tpl.get(year).value.strip())
			list_refs.add(refs)

		if tpl.name.matches(list_tpls):
			if tpl.has('1'):
				sfns = [tpl.get('1').value.strip()]
				if tpl.has('2'):
					sfns.append(tpl.get('2').value.strip())
				list_sfns.add(sfns)

	def error_print(self, error):
		error_text = 'Error "{}" on parsing footnotes of page "{}"'.format(error, self.title)
		print(error_text)
		save_error_log(filename_error_log, error_text)


def save_error_log(filename_error_log, error_text):
	import vladi_commons
	vladi_commons.file_savelines(filename_error_log, error_text)


class MakeWikiList:
	def __init__(self, pages_with_referrors, pwb_format=True, alphabet_order=True):
		self.pages_with_referrors = pages_with_referrors
		self.wikisections = []
		self.letter_groups = {
			u'А':          u'[А]',
			u'Б':          u'[Б]',
			u'ВГ':         u'[ВГ]',
			u'Д':          u'[Д]',
			u'ЕЁЖЗИЙ':     u'[ЕЁЖЗИЙ]',
			u'К':          u'[К]',
			u'ЛМ':         u'[ЛМ]',
			u'НО':         u'[НО]',
			u'П':          u'[П]',
			u'Р':          u'[Р]',
			u'С':          u'[С]',
			u'Т':          u'[Т]',
			u'УФХ':        u'[УФХ]',
			u'ЦЧШЩЪЫЬЭЮЯ': u'[ЦЧШЩЪЫЬЭЮЯ]',
			'other':       r'[^АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ]'
		}
		self.parts = {}
		for d in self.letter_groups.keys():
			self.parts[d] = {}

		self.split_parts_per_alphabet_order()
		self.make_wikilists()

		pass

	def list_formating2wikilink(self, dict):
		"""Сортировка списка по алфавиту и форматирование в викиссылки."""
		list_wikilinks = []
		for title in sorted(dict.keys()):
			page_wikilinks = []
			for ref in dict[title]:
				page_wikilinks.append(r"[[#{link}|{text}]]".format(link=ref['link_to_sfn'], text=ref['text']))
				pass
			list_wikilinks.append(r'* [[{t}]]:<br><section begin="{t}" />{all_wikilinks}<section end="{t}" />'.format(
					t=title.replace('_', ' '), all_wikilinks=', '.join(page_wikilinks)))
		return list_wikilinks

	def split_parts_per_alphabet_order(self):
		# import re
		import vladi_commons

		groups_re = vladi_commons.re_compile_dict(self.letter_groups)

		for title in sorted(self.pages_with_referrors.keys()):
			ref = self.pages_with_referrors[title]

			for group_re in groups_re:
				if group_re['c'].match(title):
					self.parts[group_re['name']][title] = ref
					break

	def make_wikilists(self, pwb_format=True, alphabet_order=True):
		global max_lines_per_file, filename_part, root_wikilists, header, marker_page_start, marker_page_end, bottom
		import vladi_commons

		# filename = 'listpages_errref_json17-1325.txt'
		# page_err_refs_full = vladi_commons.json_data_from_file(filename_listpages_errref_json)

		self.split_parts_per_alphabet_order()
		pass

		# vladi_commons.json_store_to_file(filename_part, self.parts)

		# сортировка списка по алфавиту и форматирование в викиссылки
		# self.list_formating2wikilink()
		# parts = self.list_formating2wikilink(part)
		# parts = self.list_formating2wikilink(parts)

		# разделение списка на части по числу строк
		# parts = vladi_commons.split_list_per_line_count(self.wikisections, max_lines_per_file)


		if pwb_format == True:
			result_page = ''
			save_filename = filename_part + '.txt'
			num_part = 1

			for part in self.parts:
				wikiformated_part = self.list_formating2wikilink(self.parts[part])
				pn = u'Не русские буквы' if part == 'other' else part
				pagename = u'Шаблон:' + root_wikilists + pn
				part_page_text = marker_page_start \
								 + "\n'''" + pagename + "'''\n" \
								 + header \
								 + '\n'.join(wikiformated_part) \
								 + "\n" + bottom \
								 + "\n" + marker_page_end + "\n\n"
				num_part += 1
				result_page += part_page_text
			vladi_commons.file_savetext(save_filename, result_page)
			return save_filename


		else:
			saved_filenames = []
			num_part = 1
			for part in self.parts:
				filename_part_ = filename_part + str(num_part) + '.txt'
				saved_filenames.append(filename_part_)
				vladi_commons.file_savetext(filename_part_, header)  # запись шапки списка
				vladi_commons.file_savelines(filename_part_, part, True)
				num_part += 1

			return saved_filenames


class MakeLists:
	def __init__(self):
		self.full_err_listpages = {}
		self.transcludes_sfntpls = set()
		self.transcludes_of_warning_tpl = set()
		self.listpages_with_referrors_without_warning_tpl = set()
		self.list_to_remove_warning_tpl = set()

		self.sfns_like_names = vladi_commons.str2list(names_sfn_templates)
		self.name_of_warning_tpl = warning_tpl_name

		self.filename_tpls_transcludes = filename_tpls_transcludes
		self.filename_listpages_errref = filename_listpages_errref
		self.filename_listpages_errref_json = filename_listpages_errref_json
		self.filename_list_transcludes_of_warning_tpl = filename_list_transcludes_of_warning_tpl
		self.filename_listpages_errref_where_no_yet_warning_tpl = filename_listpages_errref_where_no_yet_warning_tpl
		self.filename_list_to_remove_warning_tpl = filename_list_to_remove_warning_tpl

		self.make_list_transcludes_sfns()
		print(len(self.transcludes_sfntpls))

		if len(self.transcludes_sfntpls) > 0:
			# Создание списков страниц с ошибками
			self.make_pages_with_referrors()
			if len(self.full_err_listpages) > 0:
				self.make_list_transcludes_of_warning_tpl()
				self.make_list_to_remove_warning_tpl()
				self.make_list_to_add_warning_tpl()
			# remove_tpl_from_pages(tplname, listpages_for_remove)

	def make_pages_with_referrors(self):
		"""Создание списков страниц с ошибками

		Читать с вики-сайта список страниц с sfn-шаблонами, и сканировать их на шибки сносок.
		Или читать готовый полный список ошибок из файла JSON
		"""
		if not read_list_from_file_JSON:
			# сканирование на ошибки
			print('start scan pages')
			self.make_listpages_with_referrors()
			# referrors = MakeListpageReferrors(self.list_transcludes)
			# pages_with_referrors = referrors.pages_with_referrors
			# del referrors

			# Запись списка в файлы
			if len(self.full_err_listpages) > 0:
				pass
			vladi_commons.file_savelines(self.filename_listpages_errref,
										 self.full_err_listpages.keys())  # просто перечень страниц
			vladi_commons.json_store_to_file(self.filename_listpages_errref_json,
											 self.full_err_listpages)  # полные данные в JSON

		elif read_list_from_file_JSON:
			self.full_err_listpages = vladi_commons.json_data_from_file(self.filename_listpages_errref_json)

	def make_list_to_add_warning_tpl(self):
		"""Список куда предупреждение ещё не поставлено."""
		listpages_with_referrors = set([title for title in self.full_err_listpages])
		self.listpages_with_referrors_without_warning_tpl = listpages_with_referrors - self.transcludes_of_warning_tpl - self.list_to_remove_warning_tpl
		vladi_commons.file_savelines(self.filename_listpages_errref_where_no_yet_warning_tpl,
									 sorted(self.listpages_with_referrors_without_warning_tpl))  # сохранение списка

	def make_list_transcludes_of_warning_tpl(self):
		"""Список страниц где шаблон уже установлен."""
		# Взять с сайта - True, или из файла - False.
		if transcludes_of_warning_tpl_get_from_site:
			# from wikiapi import get_list_transcludes_of_tpls
			self.transcludes_of_warning_tpl = self.get_list_transcludes_of_tpls_from_site(self.name_of_warning_tpl)
			vladi_commons.file_savelines(self.filename_list_transcludes_of_warning_tpl,
										 sorted(self.transcludes_of_warning_tpl))
		else:
			self.transcludes_of_warning_tpl = vladi_commons.file_readlines_in_set(
					self.filename_list_transcludes_of_warning_tpl)

	def make_list_transcludes_sfns(self):
		"""Список включений sfn-шаблонов. С сайта, из файла, или указанные вручную."""
		# from wikiapi import get_list_transcludes_of_sfntpls_from_site
		global get_transcludes_from

		if get_transcludes_from == 1:  # from wikiAPI
			self.transcludes_sfntpls = self.get_list_transcludes_of_tpls_from_site(self.sfns_like_names)
			vladi_commons.file_savelines(self.filename_tpls_transcludes, self.transcludes_sfntpls)

		# Тесты
		elif get_transcludes_from == 2:  # from file
			self.transcludes_sfntpls = vladi_commons.file_readlines_in_set(self.filename_tpls_transcludes)

		elif get_transcludes_from == 3:  # from manual
			global test_pages
			self.transcludes_sfntpls = test_pages

	def get_list_transcludes_of_tpls_from_site(self, list_tempates):
		import requests
		list = set()
		for tpl in vladi_commons.str2list(list_tempates):
			url = 'http://tools.wmflabs.org/ruwikisource/WDBquery_transcludes_template/?lang=ru&format=json&template=' + quote(
					tpl)
			# GETparameters = {"action": "render"}  # html
			GETparameters = {}
			r = requests.get(url, data=GETparameters)
			list = list.union(r.json())
		return list

	def make_listpages_with_referrors(self):
		pages_count = len(self.transcludes_sfntpls)
		print(u'All pages: {}.'.format(pages_count))
		p_count_cur = pages_count

		for title in self.transcludes_sfntpls:
			global print_log
			if print_log:
				print(u'Page # {}: {}'.format(p_count_cur, title))
			page = ScanRefsOfPage(title, p_count_cur)
			if len(page.full_errrefs) > 0:
				self.full_err_listpages[title] = page.full_errrefs
			# self.collect_refs(title, p_count_cur)
			p_count_cur -= 1

	def make_list_to_remove_warning_tpl(self):
		self.list_to_remove_warning_tpl = self.transcludes_of_warning_tpl - set(
				[title for title in self.full_err_listpages])
		vladi_commons.file_savelines(self.filename_list_to_remove_warning_tpl, sorted(self.list_to_remove_warning_tpl))

	# def remove_tpl_from_changed_pages(self):
