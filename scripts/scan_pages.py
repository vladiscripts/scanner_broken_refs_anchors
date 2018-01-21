#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
from sqlite3 import IntegrityError
import time
from config import *
from scripts.db import session, Page, Ref, WarningTpls, Timecheck, queryDB
from scripts.scan_refs_of_page import ScanRefsOfPage


def do_scan():
	"""Сканирование страниц на ошибки"""
	# pages_for_scan = db_get_list_pages_for_scan()
	# for p in pages_for_scan:
	for p in db_get_list_pages_for_scan():
		page_id, page_title = p[0], p[1]

		# For tests
		# if page_id != 273920:	continue

		# очистка db от списка старых ошибок
		session.query(Ref).filter(Ref.page_id == page_id).delete()
		session.query(Timecheck).filter(Timecheck.page_id == page_id).delete()
		# session.flush()
		# сканирование страниц на ошибки
		page = ScanRefsOfPage(page_id, page_title)
		ref_no_doubles = []
		for ref in page.err_refs:
			session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
		# try:
		# 	session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
		# except IntegrityError:
		# 	pass
		# except:
		# 	pass

		# session.query(Ref).filter_by(page_id = page_id, citeref = ref['citeref']).delete()
		# if session.query(Ref).filter_by(page_id = page_id, citeref = ref['citeref']) .count() < 1:
		# 	session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
		# 	session.commit()
		# if ref['citeref'] not in ref_no_doubles:
		# 	ref_no_doubles.append(ref['citeref'])
		# 	session.merge(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
		# 	session.flush()

		# try:
		# 	session.merge(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
		# except:
		# 	pass
		# for ref in page.err_refs:
		# 	# try:
		# 	# 	x = session.query(Ref).filter_by(Ref.page_id = page_id, Ref.citeref = ref['citeref']).first()
		# 	# except:
		# 	# 	pass
		# 	x = session.query(Ref).filter_by(page_id=page_id, citeref=ref['citeref']).first()
		# 	if not x:
		# 		# 	session.query(Ref).filter(page_id=page_id, citeref=ref['citeref']).update(r)
		# 		# else:
		# 		try:
		# 			session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
		# 		except:
		# 			pass
		time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
		# session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: time_current})
		session.add(Timecheck(page_id, time_current))
		# try:
		# 	session.flush()
		# except:
		# 	pass
		# session.flush()
		session.commit()


def db_get_list_pages_for_scan():
	return queryDB(session.query(Page.page_id, Page.title) \
				   .select_from(Page) \
				   .outerjoin(Timecheck, Page.page_id == Timecheck.page_id) \
				   .filter((Timecheck.timecheck.is_(None)) | (Page.timeedit > Timecheck.timecheck)))

# return session.execute(q).fetchall()


# def db_get_list_pages_for_scan(self):
# 	# 	"""	может праильней так?
# 	# 	SELECT * FROM  pages LEFT JOIN timecheck
# 	# 	ON pages.page_id=timecheck.page_id
# 	# 	WHERE timecheck.page_id is null
# 	#
# 	# 	при объединении таблицы timecheck
# 	# 	SELECT * FROM  pages WHERE timecheck is null
# 	# 	"""
# 	q = session.query(Page.page_id, Page.title).select_from(Page).filter(
# 		(Page.timecheck.is_(None)) |
# 		(Page.timeedit > Page.timecheck))
# 	# q = session.query(Page.page_id, Page.title) \
# 	# 	.select_from(Page) \
# 	# 	.outerjoin(Timecheck, Page.page_id == Timecheck.page_id) \
# 	# 	.filter(
# 	# 	(Timecheck.timecheck.is_(None)) |
# 	# 	(Page.timeedit > Timecheck.timecheck)
# 	# )
# 	return session.execute(q).fetchall()


# for test
# page = ScanRefsOfPage('2091672', 'Марк Фульвий Флакк (консул 125 года до н. э.)')
# pass
