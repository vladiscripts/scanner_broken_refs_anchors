# coding: utf-8
#
# author: https://github.com/vladiscripts
#
from sqlalchemy.sql import update
from scripts.db import session, Page, Ref, WarningTps  # , Timecheck
import time
from config import *
from scripts import scan_refs_of_page


class MakeLists:
	full_err_listpages = {}
	transcludes_sfntpls = set()
	transcludes_of_warning_tpl = set()
	errpages_without_warning_tpl = set()
	list_to_remove_warning_tpl = set()

	# self.sfns_like_names = vladi_commons.str2list(names_sfn_templates)

	def scan_pages_with_referrors(self):
		"""Сканирование страниц на ошибки"""
		for p in self.db_get_list_pages_for_scan():
			page_id = p[0]
			page_title = p[1]

			# удаление старых ошибок в любом случае: если не обнаружены, или есть новые
			session.query(Ref).filter(Ref.page_id == page_id).delete()
			# session.query(Timecheck).filter(Timecheck.page_id == page_id).delete()

			# сканирование страниц на ошибки
			page = scan_refs_of_page.ScanRefsOfPage(page_id, page_title)
			for ref in page.full_errrefs:
				session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
			time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
			session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: time_current})
			# session.add(Timecheck(page_id, time_current))
			session.commit()

	def db_get_list_pages_for_scan(self):
		# 	"""	может праильней так?
		# 	SELECT * FROM  pages LEFT JOIN timecheck
		# 	ON pages.page_id=timecheck.page_id
		# 	WHERE timecheck.page_id is null
		#
		# 	при объединении таблицы timecheck
		# 	SELECT * FROM  pages WHERE timecheck is null
		# 	"""
		q = session.query(Page.page_id, Page.title).select_from(Page).filter(
			(Page.timecheck.is_(None)) |
			(Page.timeedit > Page.timecheck))
		# q = session.query(Page.page_id, Page.title) \
		# 	.select_from(Page) \
		# 	.outerjoin(Timecheck, Page.page_id == Timecheck.page_id) \
		# 	.filter(
		# 	(Timecheck.timecheck.is_(None)) |
		# 	(Page.timeedit > Timecheck.timecheck)
		# )
		return session.execute(q).fetchall()

	def save_listpages_to_remove_warning_tpl(self):
		query = session.query(WarningTps.title) \
			.select_from(WarningTps) \
			.outerjoin(Ref, WarningTps.page_id == Ref.page_id) \
			.filter(Ref.page_id.is_(None))

		self.list_to_remove_warning_tpl = [str(title[0]) for title in session.execute(query).fetchall()]
		file_savelines(filename_list_to_remove_warning_tpl, sorted(self.list_to_remove_warning_tpl))

	def save_listpages_to_add_warning_tpl(self):
		"""Список куда предупреждение ещё не поставлено."""
		query = session.query(Page.title).select_from(Page) \
			.outerjoin(WarningTps) \
			.join(Ref, Page.page_id == Ref.page_id) \
			.filter(WarningTps.page_id.is_(None), Ref.page_id.isnot(None)) \
			.group_by(Page.title)

		self.errpages_without_warning_tpl = [str(title[0]) for title in session.execute(query).fetchall()]
		file_savelines(filename_listpages_errref_where_no_yet_warning_tpl, self.errpages_without_warning_tpl)

	# def make_list_transcludes_of_warning_tpl(self):
	# 	"""Список страниц где шаблон уже установлен."""
	# 	# Взять с сайта - True, или из файла - False.
	# 	if transcludes_of_warning_tpl_get_from_site:
	# 		db.make_list_transcludes_from_wdb_to_sqlite()
	# 		vladi_commons.file_savelines(filename_list_transcludes_of_warning_tpl,
	# 									 sorted(self.transcludes_of_warning_tpl))
	# 	else:
	# 		self.transcludes_of_warning_tpl = vladi_commons.file_readlines_in_set(
	# 				filename_list_transcludes_of_warning_tpl)
	#
	# def make_list_transcludes_sfns(self):
	# 	"""Список включений sfn-шаблонов. С сайта, из файла, или указанные вручную."""
	# 	global get_transcludes_from
	#
	# 	if get_transcludes_from == 1:  # from wikiAPI
	# 		self.transcludes_sfntpls = self.get_list_transcludes_of_tpls_from_site(self.sfns_like_names)
	# 		vladi_commons.file_savelines(filename_tpls_transcludes, self.transcludes_sfntpls)
	#
	# 	# Тесты
	# 	elif get_transcludes_from == 2:  # from file
	# 		self.transcludes_sfntpls = vladi_commons.file_readlines_in_set(filename_tpls_transcludes)
	#
	# 	elif get_transcludes_from == 3:  # from manual
	# 		global test_pages
	# 		self.transcludes_sfntpls = test_pages
