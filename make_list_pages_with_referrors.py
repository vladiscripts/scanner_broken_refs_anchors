# coding: utf8
#
# author: https://github.com/vladiscripts
#
from urllib.parse import quote
import re
from lxml import etree, html
import time
from config import *
import vladi_commons, wikiapi
# from db import *
import db


class ScanRefsOfPage:
	def __init__(self, page_id, title,
				 # pages_count_cur,
				 ):
		# self.session = session
		self.list_sfns = set()
		self.list_refs = set()
		self.all_sfn_info_of_page = []
		self.full_errrefs = []

		self.page_id = page_id
		self.title = title
		# self.pages_count_cur = pages_count_cur
		self.parsed_html = wikiapi.page_html_parse(self.title)  # html из url
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
						# href = ''
						# text = ''
						# link_to_sfn = ''
						# href = a.attrib['href']  # href = span.xpath("*/a[contains(@href,'CITEREF')]/@href")
						# text = a.text
						# link_to_sfn = li.attrib['id']  # li.xpath("./@id")						
						a_text = re.search(r'<a [^>]*>(.*?)</a>', str(etree.tostring(a, encoding='unicode')), re.DOTALL).group(1)
			
						href_cut = self.cut_href(a.attrib['href'])
						self.list_sfns.add(href_cut)
						self.all_sfn_info_of_page.append(
								{'citeref': href_cut, 'text': a_text, 'link_to_sfn': str(li.attrib['id'])})
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
			for citeref_bad in sorted(err_refs):
				it_sfn_double = False
				for sfn in self.all_sfn_info_of_page:
					if citeref_bad == sfn['citeref'] and not it_sfn_double:
						self.full_errrefs.append(sfn)
						# db.session.add(db.Ref(self.page_id, sfn['citeref'], sfn['link_to_sfn'], sfn['text']))
						it_sfn_double = True
						# db.session.commit()

			# db.session.commit()   # коммит лучше одновременно с регистрацией в Timecheck, в вызывающей функции

		# global print_log_full
		# if print_log_full:
		# 	print('Page # {}: {}'.format(self.pages_count_cur, self.title))
		# 	# print(u'Ошибочные сноски типа sfn без связи с ref: {}'.format(self.list_pages_with_referrors[self.title]))
		# 	print('Errorious sfn-like links without anchors in refs: {}'.format(self.full_errrefs))

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
	def __init__(self,
				 # session,
				 # pwb_format=True, alphabet_order=True
				 ):
		# self.pages_with_referrors = pages_with_referrors
		# self.session = session
		# self.wikisections = []
		# self.letter_groups = {
		# 	u'А':          u'[А]',
		# 	u'Б':          u'[Б]',
		# 	u'ВГ':         u'[ВГ]',
		# 	u'Д':          u'[Д]',
		# 	u'ЕЁЖЗИЙ':     u'[ЕЁЖЗИЙ]',
		# 	u'К':          u'[К]',
		# 	u'ЛМ':         u'[ЛМ]',
		# 	u'НО':         u'[НО]',
		# 	u'П':          u'[П]',
		# 	u'Р':          u'[Р]',
		# 	u'С':          u'[С]',
		# 	u'Т':          u'[Т]',
		# 	u'УФХ':        u'[УФХ]',
		# 	u'ЦЧШЩЪЫЬЭЮЯ': u'[ЦЧШЩЪЫЬЭЮЯ]',
		# 	'other':       r'[^АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ]'
		# }
		# self.parts = {}
		# # for d in self.letter_groups.keys():
		# # 	self.parts[d] = {}
		#
		#
		#
		# self.letter_groups2 = {
		# 	u'А':          u'А',
		# 	u'Б':          u'Б',
		# 	u'ВГ':         u'ВГ',
		# 	u'Д':          u'Д',
		# 	u'ЕЁЖЗИЙ':     u'ЕЁЖЗИЙ',
		# 	u'К':          u'К',
		# 	u'ЛМ':         u'ЛМ',
		# 	u'НО':         u'НО',
		# 	u'П':          u'П',
		# 	u'Р':          u'Р',
		# 	u'С':          u'С',
		# 	u'Т':          u'Т',
		# 	u'УФХ':        u'УФХ',
		# 	u'ЦЧШЩЪЫЬЭЮЯ': u'ЦЧШЩЪЫЬЭЮЯ',
		# 	# 'other':       r'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
		# }
		# for d in self.letter_groups2:
		# 	self.parts[d] = [i for i in d]
		# # temp_d =
		# # self.parts['other']= [d. for d in self.parts.values()]
		# dict2 = []
		# for d in self.parts.values():
		# 	dict2 += d
		# self.parts['other'] = dict2
		# # [d. for d in self.parts.values()]

		# self.split_parts_per_alphabet_order()
		db.make_wikilist_titles()
		self.make_wikilists()

	# def list_formating2wikilink(self, dict):
	# 	"""Сортировка списка по алфавиту и форматирование в викиссылки."""
	# 	list_wikilinks = []
	# 	for title in sorted(dict.keys()):
	# 		page_wikilinks = []
	# 		for ref in dict[title]:
	# 			page_wikilinks.append(r"[[#{link}|{text}]]".format(link=ref['link_to_sfn'], text=ref['text']))
	# 			pass
	# 		list_wikilinks.append(r'* [[{t}]]:<br><section begin="{t}" />{all_wikilinks}<section end="{t}" />'.format(
	# 				t=title.replace('_', ' '), all_wikilinks=', '.join(page_wikilinks)))
	# 	return list_wikilinks

	def formating_sql2wikilink(self, part):
		"""Сортировка sql refs по алфавиту и форматирование в викиссылки."""
		from sqlalchemy.sql import func

		part_list_wikilinks = []
		q = db.session.query(db.Page.page_id, db.Page.title)
		# .filter(func.substr(db.Page.title, 1, 1).in_(part))

		for p in db.session.execute(q).fetchall():
			# page_wikilinks = []
			# q = db.session.query(func.substr(p.pages_title, 1, 1).in_(self.parts[part]))
			# y = db.session.execute(q).fetchall()
			# db.Ref.text.op('REGEXP')('[i]'),
			q = db.session.query(db.Ref.link_to_sfn, db.Ref.text) \
				.filter(db.Ref.page_id == p[0]) \
				.order_by(db.Ref.citeref)  # func.substr(p.pages_title, 1, 1).in_(self.parts[part])
			# for ref in db.session.execute(q).fetchall():
			# 	page_wikilinks.append(r"[[#{link}|{text}]]".format(link=ref.refs_link_to_sfn, text=ref.refs_text))
			# l = [ref for ref in db.session.execute(q).fetchall()]
			# page_wikilinks = []
			# for ref in db.session.execute(q).fetchall():
			# 	page_wikilinks = page_wikilinks + r"[[#{link}|{text}]]".format(link=ref.refs_link_to_sfn, text=ref.refs_text)
			page_wikilinks = [r"[[#{link}|{text}]]".format(link=ref.refs_link_to_sfn, text=ref.refs_text)
							  for ref in db.session.execute(q).fetchall()]
			part_list_wikilinks.append(
					r'* [[{t}]]:<br><section begin="{t}" />{all_wikilinks}<section end="{t}" />'.format(
							t=p.pages_title.replace('_', ' '), all_wikilinks=', '.join(page_wikilinks)))

		return part_list_wikilinks

	# def split_parts_per_alphabet_order(self):
	# 	# import re
	# 	from sqlalchemy.sql import join, select
	# 	import vladi_commons
	# 	import db
	#
	# 	# groups_re = vladi_commons.re_compile_dict(self.letter_groups)
	#
	# 	# for title in sorted(self.pages_with_referrors.keys()):
	# 	# 	ref = self.pages_with_referrors[title]
	# 	# 	for group_re in groups_re:
	# 	# 		if group_re['c'].match(title):
	# 	# 			self.parts[group_re['name']][title] = ref
	# 	# 			break
	#
	# 	query = db.session.query(db.Page.title, db.Ref.citeref, db.Ref.link_to_sfn, db.Ref.text) \
	# 		.select_from(db.Page).join(db.Ref) \
	# 		.group_by(db.Ref.page_id) \
	# 		.order_by(db.Ref.citeref)
	#
	# # for ref in db.session.execute(query).fetchall():
	# #
	# # 	for group_re in groups_re:
	# # 		print(ref['pages_title'])
	# # 		if group_re['c'].match(ref['pages_title']):
	# # 			self.parts[group_re['name']][ref['pages_title']] = ref
	# # 			break

	def make_wikilists(self,
					   # pwb_format=True, alphabet_order=True
					   ):
		global max_lines_per_file, filename_part, root_wikilists, header, marker_page_start, marker_page_end, bottom

		# filename = 'listpages_errref_json17-1325.txt'
		# page_err_refs_full = vladi_commons.json_data_from_file(filename_listpages_errref_json)

		# self.split_parts_per_alphabet_order()
		# pass

		# vladi_commons.json_store_to_file(filename_part, self.parts)

		# сортировка списка по алфавиту и форматирование в викиссылки
		# self.list_formating2wikilink()
		# parts = self.list_formating2wikilink(part)
		# parts = self.list_formating2wikilink(parts)

		# разделение списка на части по числу строк
		# parts = vladi_commons.split_list_per_line_count(self.wikisections, max_lines_per_file)


		# if pwb_format == True:
		# 	result_page = ''
		# 	save_filename = filename_part + '.txt'
			# num_part = 1
			#
			# for part in self.parts:
			# 	# wikiformated_part = self.list_formating2wikilink(self.parts[part])
			# 	wikiformated_part = self.formating_sql2wikilink(self.parts[part])
			# 	pn = u'Не русские буквы' if part == 'other' else part
			# 	pagename = u'Шаблон:' + root_wikilists + pn
			# 	part_page_text = marker_page_start \
			# 					 + "\n'''" + pagename + "'''\n" \
			# 					 + header \
			# 					 + '\n'.join(wikiformated_part) \
			# 					 + "\n" + bottom \
			# 					 + "\n" + marker_page_end + "\n\n"
			# 	num_part += 1
			# 	result_page += part_page_text
			# # vladi_commons.file_savetext(save_filename, result_page)
			#
			# # return save_filename
			#
			# from sqlalchemy.orm import subqueryload
			# .options(subqueryload(db.Wikilists.letter))

		save_filename = filename_part + '.txt'
		result_page = ''

		for wikilist in db.session.execute(db.session.query(db.Wikilists.title).group_by(db.Wikilists.title)).fetchall():
			wikilist_title = wikilist[0]
			part_text = ''
			# pq = db.session.query(db.Page.page_id, db.Page.title).select_from(db.Page) \
			# 	.outerjoin(db.Ref, db.Page.page_id == db.Ref.page_id)\
			# 	.filter(db.Ref.page_id != None, db.Page.wikilist == wikilist.wikilists_letter)\
			# 	.group_by(db.Ref.page_id) \
			# 	.order_by(db.Page.page_id)  # .filter(func.substr(db.Page.title, 1, 1).in_(part))
			pq = db.session.query(db.Page.page_id, db.Page.title).select_from(db.Page) \
				.join(db.Ref, db.Page.page_id == db.Ref.page_id)\
				.join(db.Wikilists, db.Wikilists.letter == db.Page.wikilist) \
				.filter(db.Ref.page_id != None, db.Wikilists.title == wikilist_title) \
				.group_by(db.Ref.page_id) \
				.order_by(db.Page.title)
			pages4check = db.session.execute(pq).fetchall()
			for p in pages4check:
				page_id = p[0]
				title = p[1]
				rq = db.session.query(db.Ref.link_to_sfn, db.Ref.text) \
					.filter(db.Ref.page_id == page_id) \
					.order_by(db.Ref.citeref)
				refs = db.session.execute(rq).fetchall()
				if len(refs) > 0:
					page_wikilinks = []
					for ref in refs:
						page_wikilinks.append(
								r"[[#{link}|{text}]]".format(link=ref.refs_link_to_sfn, text=ref.refs_text))
					part_text += '* [[{t}]]:<br><section begin="{t}" />{all_wikilinks}<section end="{t}" />\n' \
						.format(t=title.replace('_', ' '), all_wikilinks=', '.join(page_wikilinks))
					pass

			if part_text != '':
				# pn = u'Не русские буквы' if wikilist.wikilists_letter == '*' else wikilist.wikilists_title
				# pn = u'Не русские буквы' if wikilist_title == 'other' else wikilist_title
				# pagename = u'Шаблон:' + root_wikilists + pn
				pagename = u'Шаблон:' + root_wikilists + wikilist_title
				part_page_text = marker_page_start \
								 + "\n'''" + pagename + "'''\n" \
								 + header \
								 + '\n' + part_text \
								 + "\n" + bottom \
								 + "\n" + marker_page_end + "\n\n"  # + '\n'.join(part_text) \
				result_page = result_page + part_page_text

		vladi_commons.file_savetext(save_filename, result_page)
		# return save_filename










		# for part in self.parts:
		# 		# wikiformated_part = self.list_formating2wikilink(self.parts[part])
		# 		wikiformated_part = self.formating_sql2wikilink(self.parts[part])
		# 		pn = u'Не русские буквы' if part == 'other' else part
		# 		pagename = u'Шаблон:' + root_wikilists + pn
		# 		part_page_text = marker_page_start \
		# 						 + "\n'''" + pagename + "'''\n" \
		# 						 + header \
		# 						 + '\n'.join(wikiformated_part) \
		# 						 + "\n" + bottom \
		# 						 + "\n" + marker_page_end + "\n\n"
		# 		num_part += 1
		# 		result_page += part_page_text
		# 	# vladi_commons.file_savetext(save_filename, result_page)
		# 	return save_filename



		# else:
		# 	saved_filenames = []
		# 	num_part = 1
		# 	for part in self.parts:
		# 		filename_part_ = filename_part + str(num_part) + '.txt'
		# 		saved_filenames.append(filename_part_)
		# 		vladi_commons.file_savetext(filename_part_, header)  # запись шапки списка
		# 		vladi_commons.file_savelines(filename_part_, part, True)
		# 		num_part += 1
		#
		# 	return saved_filenames


class MakeLists():
	def __init__(self,
				 # session
				 ):
		# self.session = session
		self.full_err_listpages = {}
		self.transcludes_sfntpls = set()
		self.transcludes_of_warning_tpl = set()
		self.listpages_with_referrors_without_warning_tpl = set()
		self.list_to_remove_warning_tpl = set()

		self.sfns_like_names = vladi_commons.str2list(names_sfn_templates)
		self.name_of_warning_tpl = warning_tpl_name

		self.filename_tpls_transcludes = filename_tpls_transcludes
		self.filename_listpages_errref = filename_listpages_errref
		# self.filename_listpages_errref_json = filename_listpages_errref_json
		self.filename_list_transcludes_of_warning_tpl = filename_list_transcludes_of_warning_tpl
		self.filename_listpages_errref_where_no_yet_warning_tpl = filename_listpages_errref_where_no_yet_warning_tpl
		self.filename_list_to_remove_warning_tpl = filename_list_to_remove_warning_tpl

		# self.make_list_transcludes_sfns()

		if not read_from_local_db:
			db.make_list_transcludes_from_wdb_to_sqlite()

		# if len(self.transcludes_sfntpls) > 0:
		# 	# Создание списков страниц с ошибками
		# 	self.make_pages_with_referrors()
		# 	if len(self.full_err_listpages) > 0:
		# 		# self.make_list_transcludes_of_warning_tpl()
		# 		self.make_list_to_remove_warning_tpl()
		# 		self.make_list_to_add_warning_tpl()
		# 	# remove_tpl_from_pages(tplname, listpages_for_remove)


		# Создание списков страниц с ошибками
		# self.make_pages_with_referrors()
		print('start scan pages')
		self.make_listpages_with_referrors()
		self.make_list_to_remove_warning_tpl()
		self.make_list_to_add_warning_tpl()

	# remove_tpl_from_pages(tplname, listpages_for_remove)

	# def make_pages_with_referrors(self):
	# 	"""Создание списков страниц с ошибками
	#
	# 	Читать с вики-сайта список страниц с sfn-шаблонами, и сканировать их на ошибки сносок.
	# 	Или читать готовый полный список ошибок из файла JSON
	# 	"""
	# 	if not read_list_from_file_JSON:
	# 		# сканирование на ошибки
	# 		print('start scan pages')
	# 		self.make_listpages_with_referrors()
	# 		# referrors = MakeListpageReferrors(self.list_transcludes)
	# 		# pages_with_referrors = referrors.pages_with_referrors
	# 		# del referrors
	#
	# 		# Запись списка в файлы
	# 		if len(self.full_err_listpages) > 0:
	# 			pass
	# 		vladi_commons.file_savelines(self.filename_listpages_errref,
	# 									 self.full_err_listpages.keys())  # просто перечень страниц
	# 		vladi_commons.json_store_to_file(self.filename_listpages_errref_json,
	# 										 self.full_err_listpages)  # полные данные в JSON
	#
	# 	elif read_list_from_file_JSON:
	# 		self.full_err_listpages = vladi_commons.json_data_from_file(self.filename_listpages_errref_json)

	def make_list_to_add_warning_tpl(self):
		"""Список куда предупреждение ещё не поставлено."""
		# query = db.session.query(db.Page.title)\
		# 	.outerjoin(db.WarningTps).filter(db.WarningTps.id == None) \
		# 	.outerjoin(db.Ref).filter(db.Ref.page_id != None)

		# query = db.session.query(db.Page.title).select_from(db.Ref) \
		# 	.outerjoin(db.WarningTps, db.Ref.page_id == db.WarningTps.page_id) \
		# 	.join(db.Page).filter(db.WarningTps.page_id == None) \
		# 	.group_by(db.Ref.page_id)

		query = db.session.query(db.Page.title).select_from(db.Page) \
			.outerjoin(db.WarningTps) \
			.join(db.Ref, db.Page.page_id == db.Ref.page_id)\
			.filter(db.WarningTps.page_id == None, db.Ref.page_id != None) \
			.group_by(db.Page.title)
			# .order_by(db.Page.page_id, db.Ref.citeref)


		self.listpages_with_referrors_without_warning_tpl = [str(title[0]) for title in
															 db.session.execute(query).fetchall()]
		vladi_commons.file_savelines(self.filename_listpages_errref_where_no_yet_warning_tpl,
									 self.listpages_with_referrors_without_warning_tpl)

	# listpages_with_referrors = set([title for title in self.full_err_listpages])
	# self.listpages_with_referrors_without_warning_tpl = listpages_with_referrors - self.transcludes_of_warning_tpl - self.list_to_remove_warning_tpl
	# vladi_commons.file_savelines(self.filename_listpages_errref_where_no_yet_warning_tpl, sorted(self.listpages_with_referrors_without_warning_tpl))  # сохранение списка

	def make_list_transcludes_of_warning_tpl(self):
		"""Список страниц где шаблон уже установлен."""
		# Взять с сайта - True, или из файла - False.
		if transcludes_of_warning_tpl_get_from_site:
			db.make_list_transcludes_from_wdb_to_sqlite()
			# self.transcludes_of_warning_tpl = self.get_list_transcludes_of_tpls_from_site(self.name_of_warning_tpl)
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
			# self.make_list_to_remove_warning_tpl()
			self.transcludes_sfntpls = self.get_list_transcludes_of_tpls_from_site(self.sfns_like_names)
			vladi_commons.file_savelines(self.filename_tpls_transcludes, self.transcludes_sfntpls)

		# Тесты
		elif get_transcludes_from == 2:  # from file
			self.transcludes_sfntpls = vladi_commons.file_readlines_in_set(self.filename_tpls_transcludes)

		elif get_transcludes_from == 3:  # from manual
			global test_pages
			self.transcludes_sfntpls = test_pages

	# def get_list_transcludes_of_tpls_from_site(self, list_tempates):
	# 	import requests
	# 	list = set()
	# 	for tpl in vladi_commons.str2list(list_tempates):
	# 		url = 'http://tools.wmflabs.org/ruwikisource/WDBquery_transcludes_template/?lang=ru&format=json&template=' + quote(
	# 				tpl)
	# 		# GETparameters = {"action": "render"}  # html
	# 		GETparameters = {}
	# 		r = requests.get(url, data=GETparameters)
	# 		list = list.union(r.json())
	# 	return list
	#
	# def get_list_transcludes_of_tpls_from_wdb(self):
	# 	tpls = vladi_commons.str2list(self.warning_tpl_name) + vladi_commons.str2list(self.names_sfn_templates)
	# 	tpls = ['Любкер']
	# 	tpls = ','.join(['"' + t + '"' for t in tpls])
	# 	time_lastcheck = 20160910000000
	# 	sql = """SELECT
	# 			  page.page_id,
	# 			  page.page_title,
	# 			  MAX(revision.rev_timestamp) AS timestamp
	# 			FROM page
	# 			  INNER JOIN templatelinks
	# 				ON page.page_id = templatelinks.tl_from
	# 			  INNER JOIN revision
	# 				ON page.page_id = revision.rev_page
	# 			WHERE templatelinks.tl_namespace = 10
	# 			AND page.page_namespace = 0
	# 			AND templatelinks.tl_title IN (%s)
	# 			AND revision.rev_timestamp > %d
	# 			GROUP BY page.page_title
	# 			ORDER BY page.page_title""" % (tpls, time_lastcheck)
	# 	from wikiapi import wdb_query  # contents parameters: api_user, api_pw, wdb_user, wdb_pw
	# 	result = wdb_query(sql)
	#
	# 	return result

	def make_listpages_with_referrors(self):

		q = db.session.query(db.Page.page_id, db.Page.title)\
			.select_from(db.Page)\
			.outerjoin(db.Timecheck, db.Page.page_id == db.Timecheck.page_id) \
			.filter(
				(db.Timecheck.timecheck == None) |
				(db.Page.timeedit > db.Timecheck.timecheck)
		)

		# # проверка страниц с шаблоном
		# q = db.session.query(db.WarningTps.page_id, db.WarningTps.title).select_from(db.WarningTps)\
		# 	.outerjoin(db.Ref, db.WarningTps.page_id == db.Ref.page_id)\
		# 	.filter(db.Ref.page_id == None)
		#
		# # проверка страниц с кроме тех, что с шаблоном
		# q = db.session.query(db.Page.page_id, db.Page.title).select_from(db.Page)\
		# 	.outerjoin(db.WarningTps, db.WarningTps.page_id == db.Page.page_id)\
		# 	.filter(db.WarningTps.page_id == None)

		# for p in [
		# 	[555693, 'Вассерман,_Анатолий_Александрович'],
		# 	[119383, 'Росянка'],
		# 	[1652152, 'Авианосцы_типа_«Лексингтон»'],
		# 	[6459169, 'Nycticebus_linglom'],
		# ]:

		for p in db.session.execute(q).fetchall():
			page_id = p[0]
			page_title = p[1]

			# удаление старых ошибок в любом случае: если не обнаружены, или есть новые
			db.session.query(db.Ref).filter(db.Ref.page_id == page_id).delete()
			db.session.query(db.Timecheck).filter(db.Timecheck.page_id == page_id).delete()

			page = ScanRefsOfPage(page_id, page_title)
			for ref in page.full_errrefs:
				db.session.add(db.Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))

			timecheck = time.strftime('%Y%m%d%H%M%S', time.gmtime())
			db.session.add(db.Timecheck(page_id, timecheck))
			db.session.commit()

		pass

	def make_list_to_remove_warning_tpl(self):
		# self.list_to_remove_warning_tpl = self.transcludes_of_warning_tpl - set([title for title in self.full_err_listpages])
		# query = db.session.query(db.WarningTps.title).outerjoin(db.Page, db.WarningTps.id == db.Page.id).filter(				db.Page.id == None)
		query = db.session.query(db.WarningTps.title)\
			.select_from(db.WarningTps)\
			.outerjoin(db.Ref, db.WarningTps.page_id == db.Ref.page_id)\
			.filter(db.Ref.page_id == None)

		self.list_to_remove_warning_tpl = [str(title[0]) for title in db.session.execute(query).fetchall()]
		vladi_commons.file_savelines(self.filename_list_to_remove_warning_tpl, sorted(self.list_to_remove_warning_tpl))
