# coding: utf-8
#
# author: https://github.com/vladiscripts
#
from scripts.db import db_session, Page, ErrRef, WarningTpls, queryDB
from config import *


def save_listpages_to_remove_warning_tpl():
	query = db_session.query(WarningTpls.title) \
		.outerjoin(ErrRef, WarningTpls.page_id == ErrRef.page_id) \
		.filter(ErrRef.page_id.is_(None))

	list_to_remove_warning_tpl = (str(title[0]) for title in queryDB(query))
	file_savelines(filename_list_to_remove_warning_tpl, sorted(list_to_remove_warning_tpl))


def save_listpages_to_add_warning_tpl():
	"""Список куда предупреждение ещё не поставлено."""
	query = db_session.query(Page.title).select_from(Page) \
		.outerjoin(WarningTpls) \
		.join(ErrRef, Page.page_id == ErrRef.page_id) \
		.filter(WarningTpls.page_id.is_(None), ErrRef.page_id.isnot(None)) \
		.group_by(Page.title)

	errpages_without_warning_tpl = (str(title[0]) for title in queryDB(query))
	file_savelines(filename_listpages_errref_where_no_yet_warning_tpl, errpages_without_warning_tpl)


def file_savelines(filename, strlist, append=False):
	mode = 'a' if append else 'w'
	text = '\n'.join(strlist)
	with open(filename, mode, encoding='utf-8') as f:
		f.write(text)


def file_savetext(filename, text):
	with open(filename, 'w', encoding='utf-8') as f:
		f.write(text)
