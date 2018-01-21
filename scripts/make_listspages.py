# coding: utf-8
#
# author: https://github.com/vladiscripts
#
from sqlalchemy.sql import update
from scripts.db import session, Page, Ref, WarningTpls, Timecheck, queryDB
import time
from config import *


# class MakeLists:
# full_err_listpages = {}
# transcludes_sfntpls = set()
# transcludes_of_warning_tpl = set()
# errpages_without_warning_tpl = set()
# list_to_remove_warning_tpl = set()

# self.sfns_like_names = vladi_commons.str2list(names_sfn_templates)

def save_listpages_to_remove_warning_tpl():
	query = session.query(WarningTpls.title) \
		.select_from(WarningTpls) \
		.outerjoin(Ref, WarningTpls.page_id == Ref.page_id) \
		.filter(Ref.page_id.is_(None))

	list_to_remove_warning_tpl = (str(title[0]) for title in queryDB(query))
	file_savelines(filename_list_to_remove_warning_tpl, sorted(list_to_remove_warning_tpl))


def save_listpages_to_add_warning_tpl():
	"""Список куда предупреждение ещё не поставлено."""
	query = session.query(Page.title).select_from(Page) \
		.outerjoin(WarningTpls) \
		.join(Ref, Page.page_id == Ref.page_id) \
		.filter(WarningTpls.page_id.is_(None), Ref.page_id.isnot(None)) \
		.group_by(Page.title)

	errpages_without_warning_tpl = (str(title[0]) for title in queryDB(query))
	file_savelines(filename_listpages_errref_where_no_yet_warning_tpl, errpages_without_warning_tpl)

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
