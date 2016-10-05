# -*- coding: utf-8 -*-
from config import *
import vladi_commons
import wikiapi
import make_list_pages_with_referrors
import urllib.parse
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import mapper, relationship
from sqlalchemy import Table, Column, Integer, String, ForeignKey
from sqlalchemy.sql import join, select

Base = declarative_base()


def create_session(config):
	from sqlalchemy import create_engine
	from sqlalchemy.orm import sessionmaker
	db_engine = create_engine(config, echo=print_log,
							  # encoding = 'utf8', convert_unicode = True
							  )
	# from sqlalchemy import MetaData
	# metadata = MetaData()
	# metadata.create_all(db_engine)
	Base.metadata.create_all(db_engine)
	# начинаем новую сессию работы с БД
	Session = sessionmaker(bind=db_engine)
	session = Session()
	return session


class Page(Base):
	__tablename__ = 'pages'
	page_id = Column(Integer, primary_key=True, unique=True)
	title = Column(String, unique=True)  # index=True
	timeedit = Column(Integer)
	wikilist = Column(String, index=True)

	# refs = relationship("Ref")

	def __init__(self, page_id, title, timeedit):
		import re
		self.page_id = page_id
		self.title = title
		self.timeedit = timeedit
		fl = title[0:1].upper()
		self.wikilist = '*' if re.match(r'[^АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ]', fl) else fl


class Timecheck(Base):
	__tablename__ = 'timecheck'
	page_id = Column(Integer, ForeignKey('pages.page_id'), primary_key=True, unique=True)
	timecheck = Column(Integer)

	def __init__(self, page_id, timecheck):
		self.page_id = page_id
		self.timecheck = timecheck


class Ref(Base):
	__tablename__ = 'refs'
	id = Column(Integer, primary_key=True,
				# autoincrement=True
				)
	page_id = Column(Integer, ForeignKey('pages.page_id'), index=True)
	citeref = Column(String)
	link_to_sfn = Column(String)
	text = Column(String)

	def __init__(self, page_id, citeref, link_to_sfn, text):
		self.page_id = page_id
		self.citeref = citeref
		self.link_to_sfn = link_to_sfn
		self.text = text


class WarningTps(Base):
	__tablename__ = 'warnings'
	page_id = Column(Integer, ForeignKey('pages.page_id'), ForeignKey('refs.page_id'), primary_key=True, unique=True)
	title = Column(String, unique=True)

	def __init__(self, page_id, title):
		self.page_id = page_id
		self.title = title


class Wikilists(Base):
	__tablename__ = 'wikilists'
	letter = Column(String, ForeignKey('pages.wikilist'), primary_key=True, unique=True)
	title = Column(String)

	def __init__(self, letter, title):
		self.letter = letter
		self.title = title


session = create_session('sqlite:///pagesrefs.sqlite')  # ('sqlite:///:memory:')

wikilists = [
	['А', 'А'],
	['Б', 'Б'],
	['В', 'ВГ'], ['Г', 'ВГ'],
	['Д', 'Д'],
	['Е', 'ЕЁЖЗИЙ'], ['Ё', 'ЕЁЖЗИЙ'], ['Ж', 'ЕЁЖЗИЙ'], ['З', 'ЕЁЖЗИЙ'], ['И', 'ЕЁЖЗИЙ'], ['Й', 'ЕЁЖЗИЙ'],
	['К', 'К'],
	['Л', 'ЛМ'], ['М', 'ЛМ'],
	['Н', 'НО'], ['О', 'НО'],
	['П', 'П'],
	['Р', 'Р'],
	['С', 'С'],
	['Т', 'Т'],
	['У', 'УФХ'], ['Ф', 'УФХ'], ['Х', 'УФХ'],
	['Ц', 'ЦЧШЩЪЫЬЭЮЯ'], ['Ч', 'ЦЧШЩЪЫЬЭЮЯ'], ['Ш', 'ЦЧШЩЪЫЬЭЮЯ'], ['Щ', 'ЦЧШЩЪЫЬЭЮЯ'], ['Ъ', 'ЦЧШЩЪЫЬЭЮЯ'],
	['Ы', 'ЦЧШЩЪЫЬЭЮЯ'], ['Ь', 'ЦЧШЩЪЫЬЭЮЯ'], ['Э', 'ЦЧШЩЪЫЬЭЮЯ'], ['Ю', 'ЦЧШЩЪЫЬЭЮЯ'], ['Я', 'ЦЧШЩЪЫЬЭЮЯ'],
	['*', 'Не русские буквы'],
	# ['*', 'other'],
]
for r in wikilists:
	session.merge(Wikilists(r[0], r[1]))
session.commit()


def make_list_transcludes_from_wdb_to_sqlite():
	tpls_str = 'AND ' + ' OR '.join(
			['tl_title LIKE "' + wikiapi.normalization_pagename(t) + '"'
			 for t in vladi_commons.str2list(warning_tpl_name)])
	sql = """SELECT page_id, page_title
			FROM page
			JOIN templatelinks ON templatelinks.tl_from = page.page_id
				WHERE tl_namespace = 10
				%s
				AND page_namespace = 0""" % tpls_str

	# result = [
	# 	[2, b'\xd0\x9c\xd0\xbe\xd0\xb9\xd1\x80\xd1\x8b'],
	# 	[3, b'\xd0\x9c\xd0\xbe\x20\xd0\xb9\xd1\x80\xd1\x8b'],
	# 	[10, b'\xd0\x9c\xd0\xbe'],
	# ]

	session.query(WarningTps).delete()
	result = wikiapi.wdb_query(sql)
	for r in result:
		row = WarningTps(r[0], vladi_commons.byte2utf(r[1]))
		session.add(row)
	session.commit()

	# включения sfn-likes
	tpls = names_sfn_templates
	# tpls = ['sfn0']
	tpls_str = 'AND ' + ' OR '.join(['templatelinks.tl_title LIKE "' + wikiapi.normalization_pagename(t) + '"'
									  for t in vladi_commons.str2list(tpls)])
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
			ORDER BY page.page_title""" % (tpls_str)

	# result = [
	# 	[1, b'\xd0\x98\xd1\x82', b'20160915124831'],
	# 	[2, b'\xd0\x9c\xd0\xbe\xd0\xb9\xd1\x80\xd1\x8b', b'20160915124831'],
	# 	[3, b'\xd0\x9c\xd0\xbe\x20\xd0\xb9\xd1\x80\xd1\x8b', b'20160915124831'],
	# 	[4, b'\x5f\xd0\x9c\xd0\xbe\xd0\xb9', b'20160915124831'],
	# ]

	result = wikiapi.wdb_query(sql)
	session.query(Page).delete()
	for r in result:
		title = vladi_commons.byte2utf(r[1])
		row = Page(r[0], title, int(r[2]))  # time_lastcheck
		session.add(row)
	session.commit()

	# чистка PageTimecheck от записей которых нет в pages
	q = session.query(Timecheck.page_id).select_from(Timecheck).outerjoin(Page).filter(Page.page_id == None)
	for r in session.execute(q).fetchall():
		session.query(Timecheck).filter(Timecheck.page_id == r[0]).delete()
	session.commit()

	# чистка Ref
	q = session.query(Ref.page_id).select_from(Ref).outerjoin(Page).filter(Page.page_id == None)
	for r in session.execute(q).fetchall():
		session.query(Ref).filter(Ref.page_id == r[0]).delete()
	session.commit()


# make_list_transcludes_from_wdb_to_sqlite()









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
"""
