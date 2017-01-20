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
import db


class ScanRefsOfPage:
	def __init__(self, page_id, title):
		self.list_sfns = set()
		self.list_refs = set()
		self.all_sfn_info_of_page = []
		self.full_errrefs = []

		self.page_id = page_id
		self.title = title
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
						a_text = re.search(r'<a [^>]*>(.*?)</a>', str(etree.tostring(a, encoding='unicode')), re.DOTALL).group(1)
			
						href_cut = self.cut_href(a.attrib['href'])
						self.list_sfns.add(href_cut)
						self.all_sfn_info_of_page.append(
								{'citeref': href_cut, 'text': a_text, 'link_to_sfn': str(li.attrib['id'])})
						pass

		except Exception as error:
			self.error_print(error)

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

	def find_refs_via_wikiparser(self, tpl):
		"""	Поиск сносок по html-тэгу "CITEREF". """
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
	def __init__(self):
		db.make_wikilist_titles()
		self.make_wikilists()

	def formating_sql2wikilink(self, part):
		"""Сортировка sql refs по алфавиту и форматирование в викиссылки."""
		from sqlalchemy.sql import func

		part_list_wikilinks = []
		q = db.session.query(db.Page.page_id, db.Page.title)

		for p in db.session.execute(q).fetchall():
			q = db.session.query(db.Ref.link_to_sfn, db.Ref.text) \
				.filter(db.Ref.page_id == p[0]) \
				.order_by(db.Ref.citeref) 
			page_wikilinks = [r"[[#{link}|{text}]]".format(link=ref.refs_link_to_sfn, text=ref.refs_text)
							  for ref in db.session.execute(q).fetchall()]
			part_list_wikilinks.append(
					r'* [[{t}]]:<br><section begin="{t}" />{all_wikilinks}<section end="{t}" />'.format(
							t=p.pages_title.replace('_', ' '), all_wikilinks=', '.join(page_wikilinks)))

		return part_list_wikilinks

	def make_wikilists(self):
		global max_lines_per_file, filename_part, root_wikilists, header, marker_page_start, marker_page_end, bottom

		save_filename = filename_part + '.txt'
		result_page = ''

		for wikilist in db.session.execute(db.session.query(db.Wikilists.title).group_by(db.Wikilists.title)).fetchall():
			wikilist_title = wikilist[0]
			part_text = ''
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
				pagename = u'Шаблон:' + root_wikilists + wikilist_title
				part_page_text = marker_page_start \
								 + "\n'''" + pagename + "'''\n" \
								 + header \
								 + '\n' + part_text \
								 + "\n" + bottom \
								 + "\n" + marker_page_end + "\n\n"  # + '\n'.join(part_text) \
				result_page = result_page + part_page_text

		vladi_commons.file_savetext(save_filename, result_page)

		
class MakeLists():
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
		self.filename_list_transcludes_of_warning_tpl = filename_list_transcludes_of_warning_tpl
		self.filename_listpages_errref_where_no_yet_warning_tpl = filename_listpages_errref_where_no_yet_warning_tpl
		self.filename_list_to_remove_warning_tpl = filename_list_to_remove_warning_tpl

		if not read_from_local_db:
			db.make_list_transcludes_from_wdb_to_sqlite()

		# Создание списков страниц с ошибками
		print('start scan pages')
		self.make_listpages_with_referrors()
		self.make_list_to_remove_warning_tpl()
		self.make_list_to_add_warning_tpl()

	def make_list_to_add_warning_tpl(self):
		"""Список куда предупреждение ещё не поставлено."""
		query = db.session.query(db.Page.title).select_from(db.Page) \
			.outerjoin(db.WarningTps) \
			.join(db.Ref, db.Page.page_id == db.Ref.page_id)\
			.filter(db.WarningTps.page_id == None, db.Ref.page_id != None) \
			.group_by(db.Page.title)

		self.listpages_with_referrors_without_warning_tpl = [str(title[0]) for title in
															 db.session.execute(query).fetchall()]
		vladi_commons.file_savelines(self.filename_listpages_errref_where_no_yet_warning_tpl,
									 self.listpages_with_referrors_without_warning_tpl)

	def make_list_transcludes_of_warning_tpl(self):
		"""Список страниц где шаблон уже установлен."""
		# Взять с сайта - True, или из файла - False.
		if transcludes_of_warning_tpl_get_from_site:
			db.make_list_transcludes_from_wdb_to_sqlite()
			vladi_commons.file_savelines(self.filename_list_transcludes_of_warning_tpl,
										 sorted(self.transcludes_of_warning_tpl))
		else:
			self.transcludes_of_warning_tpl = vladi_commons.file_readlines_in_set(
					self.filename_list_transcludes_of_warning_tpl)

	def make_list_transcludes_sfns(self):
		"""Список включений sfn-шаблонов. С сайта, из файла, или указанные вручную."""
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

	def make_listpages_with_referrors(self):

		q = db.session.query(db.Page.page_id, db.Page.title)\
			.select_from(db.Page)\
			.outerjoin(db.Timecheck, db.Page.page_id == db.Timecheck.page_id) \
			.filter(
				(db.Timecheck.timecheck == None) |
				(db.Page.timeedit > db.Timecheck.timecheck)
		)


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

	def make_list_to_remove_warning_tpl(self):
		query = db.session.query(db.WarningTps.title)\
			.select_from(db.WarningTps)\
			.outerjoin(db.Ref, db.WarningTps.page_id == db.Ref.page_id)\
			.filter(db.Ref.page_id == None)

		self.list_to_remove_warning_tpl = [str(title[0]) for title in db.session.execute(query).fetchall()]
		vladi_commons.file_savelines(self.filename_list_to_remove_warning_tpl, sorted(self.list_to_remove_warning_tpl))
