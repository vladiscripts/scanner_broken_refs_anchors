# coding: utf-8
# author: https://github.com/vladiscripts
#
from sqlalchemy.sql import null
import pymysql.cursors
from config import *
from scripts.db import session, Page, Ref, WarningTps  # , Timecheck
# from passwords import __api_user, __api_pw, __wdb_user, __wdb_pw
import passwords


# import vladi_commons.passwords as pw  # contents parameters: api_user, api_pw, wdb_user, wdb_pw


class UpdateDB:
	def __init__(self):
		# обновить список страниц, имеющих установленный шаблон
		self.update_listpages_has_WarningTpl()

		# обновить список страниц, имеющих шаблоны типа {{sfn}}
		self.update_transcludes_sfn_tempates()

		# Опциональные чистки, проще удалить и пересоздать файл базы данных
		if clear_check_pages_with_warnings:
			# удаление метки проверки у страниц имеющих warning-шаблон
			self.drop_check_pages_with_warnings()
		if clear_all_check_pages:
			# сброс всех меток проверки
			self.drop_all_check_pages()

		# чистка PageTimecheck и Ref от записей которых нет в pages
		self.drop_depricated_by_timecheck()
		self.drop_ref()

	def update_listpages_has_WarningTpl(self):
		"""Обновить список страниц имеющих установленный шаблон."""
		tpls_str = 'AND ' + ' OR '.join(
			['tl_title LIKE "' + self.normalization_pagename(t) + '"'
			 for t in self.str2list(warning_tpl_name)])
		sql = """SELECT page_id, page_title
				FROM page
				JOIN templatelinks ON templatelinks.tl_from = page.page_id
					WHERE tl_namespace = 10
					%s
					AND page_namespace = 0;""" % tpls_str

		result = self.wdb_query(sql)
		session.query(WarningTps).delete()
		for r in result:
			row = WarningTps(r[0], self.byte2utf(r[1]))
			session.add(row)
		session.commit()

	def update_transcludes_sfn_tempates(self):
		"""Обновить список страниц, имеющих шаблоны типа {{sfn}}."""
		tpls = names_sfn_templates
		tpls_str = 'AND ' + ' OR '.join(['templatelinks.tl_title LIKE "' + self.normalization_pagename(t) + '"'
										 for t in self.str2list(tpls)])
		sql = """SELECT
				  page.page_id,
				  page.page_title,
				  MAX(revision.rev_timestamp) AS timestamp
				FROM page
				  INNER JOIN templatelinks
					ON page.page_id = templatelinks.tl_from
				  INNER JOIN revision
					ON page.page_id = revision.rev_page
				WHERE templatelinks.tl_namespace = 10
				AND page.page_namespace = 0
				%s
				GROUP BY page.page_title
				ORDER BY page.page_title;""" % (tpls_str)

		result = self.wdb_query(sql)
		session.query(Page).delete()
		for r in result:
			title = self.byte2utf(r[1])
			row = Page(r[0], title, null(), int(r[2]), null())  # time_lastcheck
			session.add(row)
		session.commit()

	# @staticmethod
	# def drop_depricated_by_timecheck():
	# 	# если в pages нет записи о статьи, то удалить и строки из timecheck?
	# 	# не нужно при объединении таблиц pages и timecheck
	# 	q = session.query(Timecheck.page_id).select_from(Timecheck).outerjoin(Page).filter(
	# 		Page.page_id.is_(None))
	# 	for r in session.execute(q).fetchall():
	# 		session.query(Timecheck).filter(Timecheck.page_id == r[0]).delete()
	# 	session.commit()
	# 	"""	может праильней так?
	# 	SELECT * FROM  pages LEFT JOIN timecheck
	# 	ON pages.page_id=timecheck.page_id
	# 	WHERE timecheck.page_id is null
	#
	# 	при объединении таблицы timecheck
	# 	SELECT * FROM  pages WHERE timecheck is null
	# 	"""



	@staticmethod
	def drop_ref():
		q = session.query(Ref.page_id).select_from(Ref).outerjoin(Page).filter(Page.page_id.is_(None))
		for r in session.execute(q).fetchall():
			session.query(Ref).filter(Ref.page_id == r[0]).delete()
		session.commit()

	# Helpers
	@staticmethod
	def drop_check_pages_with_warnings():
		"""Удаление метки проверки у страниц имеющих warning-шаблон."""
		# for r in session.execute(session.query(WarningTps.page_id)).fetchall():
		# 	# session.query(Timecheck).filter(Timecheck.page_id == r[0]).delete()
		# 	session.query(Page).filter(Page.page_id == str(r)).update({Page.timecheck: null()})
		wp = session.query(WarningTps.page_id).subquery()
		session.query(Page).filter(Page.page_id.in_(wp)). \
			update({Page.timecheck: null()}, synchronize_session="fetch")
		session.commit()

	@staticmethod
	def drop_all_check_pages():
		"""Удаление метки проверки у страниц имеющих warning-шаблон."""
		# session.query(Timecheck).delete()
		session.query(Page).update({Page.timecheck: null()})
		session.commit()

	@staticmethod
	def str2list(string):
		"""Строку в список"""
		return [string] if isinstance(string, str) else string

	@staticmethod
	def byte2utf(string):
		import urllib.parse
		string = urllib.parse.quote_from_bytes(string)
		string = urllib.parse.unquote(string, encoding='utf8')
		return string

	@staticmethod
	def normalization_pagename(t):
		""" Первая буква в верхний регистр, ' ' → '_' """
		t = t.strip()
		return t[0:1].upper() + t[1:].replace(' ', '_')

	@staticmethod
	def wdb_query(sql):
		connection = pymysql.connect(
			# Для доступа к wiki-БД с ПК необходим ssh-тунель с перебросом порта с localhost
			# ssh -L 4711:ruwiki.labsdb:3306 <username>@login.tools.wmflabs.org -i "<path/to/key>"
			# см. https://wikitech.wikimedia.org/wiki/Help:Tool_Labs/Database#Connecting_to_the_database_replicas_from_your_own_computer
			# host='127.0.0.1', port=4711,
			# или для доступа из скриптов на tools.wmflabs.org напрямую:
			# host='ruwiki.labsdb', port=3306,
			host='127.0.0.1' if run_local_not_from_wmlabs else 'ruwiki.labsdb',
			port=4711 if run_local_not_from_wmlabs else 3306,
			db='ruwiki_p',
			# user=passwords.__wdb_user,
			# password=passwords.__wdb_pw,
			user=passwords.wdb_user,
			password=passwords.wdb_pw,
			use_unicode=True, charset="utf8")
		try:
			with connection.cursor() as cursor:
				cursor.execute(sql)
			result = cursor.fetchall()
		finally:
			connection.close()
		return result


"""
-- SELECT * FROM warning_tpls_transcludes
-- JOIN pages ON warning_tpls_transcludes.page_id = pages.id
-- JOIN timecheck ON timecheck.page_id = pages.id
-- LEFT OUTER JOIN refs USING (page_id)
-- WHERE refs.page_id IS NULL

-- SELECT * FROM pages
-- LEFT OUTER JOIN warning_tpls_transcludes ON pages.id = warning_tpls_transcludes.page_id
-- LEFT OUTER JOIN refs ON pages.id = refs.page_id
-- WHERE warning_tpls_transcludes.page_id IS NULL
-- AND refs.page_id  IS NOT NULL
-- GROUP BY pages.id

-- с новыми правками или без проверки
-- SELECT * FROM pages JOIN timecheck ON pages.page_id = timecheck.page_id
-- WHERE pages.timeedit > timecheck.timecheck OR timecheck.timecheck IS NULL

-- pages без warning
-- SELECT * FROM pages LEFT OUTER JOIN warnings ON pages.page_id = warnings.page_id WHERE warnings.page_id IS NULL

-- warnings без refs, к снятию warnings
-- SELECT * FROM warnings LEFT OUTER JOIN refs ON warnings.page_id = refs.page_id WHERE  refs.page_id IS NULL

-- titles for add warnings
-- SELECT pages.title FROM pages LEFT OUTER JOIN warnings ON warnings.page_id = pages.page_id
-- JOIN refs ON pages.page_id = refs.page_id
-- WHERE  warnings.page_id IS NULL AND refs.page_id  IS NOT NULL
-- -- ORDER BY pages.page_id, refs.citeref
-- GROUP BY pages.title

--- pages with errrefs
-- SELECT * FROM refs  GROUP BY refs.page_id
--- pages with errrefs and pagnames
SELECT * FROM pages LEFT OUTER JOIN  refs ON pages.page_id = refs.page_id
WHERE refs.page_id  IS NOT NULL
GROUP BY refs.page_id

-- LEFT OUTER JOIN warnings ON warnings.page_id = refs.page_id
-- JOIN pages ON warnings.page_id = refs.page_id
-- WHERE  warnings.page_id IS NULL
-- ORDER BY warnings.page_id, refs.page_id
-- -- JOIN timecheck USING (page_id)
-- -- ORDER BY warnings.page_id, refs.page_id
-- -- GROUP BY warnings.page_id


-- DELETE FROM timecheck WHERE page_id IN (
-- SELECT page_id, title
-- FROM warning_tpls_transcludes
-- LEFT OUTER JOIN refs USING (page_id)
-- JOIN pages ON pages.id = refs.page_id
-- WHERE refs.page_id IS NULL
-- GROUP BY refs.page_id
-- )


SELECT * FROM pages JOIN refs USING (page_id) JOIN timecheck USING (page_id) WHERE title LIKE 'Росянка'
-- SELECT refs.page_id FROM refs LEFT OUTER JOIN pages WHERE  pages.page_id IS NULL

-- удаление timecheck у страниц с warnings
-- DELETE FROM timecheck WHERE timecheck.page_id IN (
-- SELECT page_id FROM warnings
--  )

-- удаление timecheck у страниц с refs
-- DELETE FROM timecheck WHERE timecheck.page_id IN (SELECT page_id FROM refs GROUP BY page_id  )


-- SELECT * FROM pages JOIN refs USING (page_id) JOIN timecheck USING (page_id)
-- WHERE title LIKE 'Росянка'


-- move timecheck.timecheck → pages.timecheck
-- UPDATE pages SET timecheck = (SELECT timecheck.timecheck FROM timecheck WHERE pages.page_id = timecheck.page_id)
"""
