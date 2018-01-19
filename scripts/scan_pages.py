#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import time
from config import *
from scripts.db import session, Page, Ref, WarningTpls  # , Timecheck
from scripts.scan_refs_of_page import ScanRefsOfPage


def do_scan():
	"""Сканирование страниц на ошибки"""
	q = session.query(Page.page_id, Page.title).select_from(Page).filter(
		(Page.timecheck.is_(None)) |
		(Page.timeedit > Page.timecheck))
	list_pages_for_scan = session.execute(q).fetchall()

	for p in list_pages_for_scan:
		page_id = p[0]
		page_title = p[1]

		# очистка db от списка старых ошибок
		session.query(Ref).filter(Ref.page_id == page_id).delete()
		# session.query(Timecheck).filter(Timecheck.page_id == page_id).delete()
		session.commit()

		# сканирование страниц на ошибки
		page = ScanRefsOfPage(page_id, page_title)
		for ref in page.err_refs:
			r = Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text'])
			x = session.query(Ref).filter_by(page_id=page_id, citeref=ref['citeref']).first()
			if not x:
				# 	session.query(Ref).filter(page_id=page_id, citeref=ref['citeref']).update(r)
				# else:
				session.add(r)
		session.flush()
		time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
		session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: time_current})
		# session.add(Timecheck(page_id, time_current))
		session.commit()

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
