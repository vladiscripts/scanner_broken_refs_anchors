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
	from sqlalchemy import MetaData
	# engine = create_engine(config['DATABASE_URI'])
	# engine = create_engine('sqlite:///:memory:', echo=True)
	db_engine = create_engine(config, echo=True,
							  # encoding = 'utf8', convert_unicode = True
							  )
	# создадём таблицы
	# metadata = MetaData()
	# metadata.create_all(db_engine)
	Base.metadata.create_all(db_engine)
	# начинаем новую сессию работы с БД
	Session = sessionmaker(bind=db_engine)
	session = Session()
	# session._model_changes = {}
	return session


class Page(Base):
	__tablename__ = 'pages'
	id = Column('id', Integer, primary_key=True, unique=True)
	title = Column('title', String, unique=True, index=True)
	timeedit = Column('timeedit', Integer)
	timecheck = Column('timecheck', Integer)
	wikilist = Column('wikilist', String)

	# refs = relationship("Ref")

	def __init__(self, id, title, timeedit, timecheck, wikilist):
		self.id = id
		self.title = title
		self.timeedit = timeedit
		self.timecheck = timecheck
		self.wikilist = wikilist


class Ref(Base):
	__tablename__ = 'refs'
	id = Column('id', Integer, primary_key=True, autoincrement=True)
	page_id = Column('page_id', Integer, ForeignKey('pages.id'))
	citeref = Column('citeref', String, unique=True)
	link_to_sfn = Column('link_to_sfn', String)
	text = Column('text', String)

	def __init__(self, page_id, citeref, link_to_sfn, text):
		self.page_id = page_id
		self.citeref = citeref
		self.link_to_sfn = link_to_sfn
		self.text = text


class WarningTps(Base):
	__tablename__ = 'warning_tps_transcludes'
	id = Column('page_id', Integer, ForeignKey('pages.id'), primary_key=True, unique=True)
	title = Column('title', String, unique=True)

	def __init__(self, id, title):
		self.id = id
		self.title = title


class Wikilists(Base):
	__tablename__ = 'wikilists'
	letter = Column('letter', String, ForeignKey('pages.wikilist'), primary_key=True, unique=True)
	title = Column('title', String)

	def __init__(self, letter, title):
		self.letter = letter
		self.title = title


# session = create_session('sqlite:///:memory:')
session = create_session('sqlite:///pagesrefs.sqlite')

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
]
for r in wikilists:
	session.merge(Wikilists(r[0], r[1]))
session.commit()

# 'other':       r'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'


# WarningTps.__table__.drop(session.bind)

def make_list_transcludes_from_wdb_to_sqlite():
	# tpls = vladi_commons.str2list(tpls)
	# tpls = vladi_commons.str2list(self.warning_tpl_name) + vladi_commons.str2list(self.names_sfn_templates)
	tpls = ['Любкер']

	# включения шаблон-предупреждения
	tpls = ','.join(['"' + t + '"' for t in vladi_commons.str2list(warning_tpl_name)])
	sql = """SELECT page_id, page_title
			FROM page
			JOIN templatelinks ON tl_from = page_id
				WHERE tl_namespace = 10	AND tl_title IN (%s)
				AND page_namespace = 0""" % tpls
	# result = wikiapi.wdb_query(sql)

	session.query(WarningTps).delete()

	result = [
		[2, b'\xd0\x9c\xd0\xbe\xd0\xb9\xd1\x80\xd1\x8b', b'20160915124831'],
		[3, b'\xd0\x9c\xd0\xbe\x20\xd0\xb9\xd1\x80\xd1\x8b', b'20160915124831'],
	]

	for r in result:
		row = WarningTps(r[0], vladi_commons.byte2utf(r[1]))
		session.add(row)
	# print(r[0], r, int(r[2]))
	# session.commit()

	# включения sfn-likes
	tpls = ','.join(['"' + t + '"' for t in vladi_commons.str2list(names_sfn_templates)])
	tpls = ['Любкер']
	time_lastcheck = 20160910000000
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
			AND templatelinks.tl_title IN (%s)
			AND revision.rev_timestamp > %d
			GROUP BY page.page_title
			ORDER BY page.page_title""" % (tpls, time_lastcheck)
	# result = wdb_query(sql)

	result = [
		[1, b'\xd0\x98\xd0\xbd\xd1\x86\xd0\xb5\xd1\x81\xd1\x82', b'20160915124831'],
		[2, b'\xd0\x9c\xd0\xbe\xd0\xb9\xd1\x80\xd1\x8b', b'20160915124831'],
		[3, b'\xd0\x9c\xd0\xbe\x20\xd0\xb9\xd1\x80\xd1\x8b', b'20160915124831'],
		# [4, "Пе́тя", 8888],
		# [5, "14\"/45_BL_Mark_VII", b'20160915124831'],
	]

	# result = get_list_transcludes_of_tpls_from_wdb()

	for r in result:
		title = vladi_commons.byte2utf(r[1])
		row = Page(r[0], title, int(r[2]), 20160910000000, title[0:1])
		# session.add(row)
		session.merge(row)
	session.commit()

	return result


make_list_transcludes_from_wdb_to_sqlite()

# таким образом можно добавить новый элемент
# new_page = Page(2, "14\"/45_BL_Mark_VII", 20160910000000)
# new_ref = Ref(2, "CITEREF.D0.91.D0.B0.D0.BB.D0.B0.D0.BA.D0.B8.D0.BD.2C_.D0.94.D0.B0.D1.88.D1.8C.D1.8F.D0.BD2006",
# 			  "cite_note-.D0.91.D0.B0.D0.BB.D0.B0.D0.BA.D0.B8.D0.BD.2C_.D0.94.D0.B0.D1.88.D1.8C.D1.8F.D0.BD.E2.80.942006.E2.80.94.E2.80.94238-1",
# 			  "Балакин, Дашьян, 2006")
# # session.add(new_page)
# session.add(new_ref)

# посмотрим что уже есть в базе данных
# for instance in session.query(Page).order_by(Page.page_id):
# 	print(instance.page_id, instance.title)
# for instance in session.query(Ref).order_by(Ref.page_id):
# 	print(instance.page_id, instance.citeref)

# print(session.query(Page).count())

# совершаем транзакцию
session.commit()

# query = select([Page.page_id, Page.title, Page.timeedit]).select_from(Page)
# r = session.execute(query).fetchall()

# join_obj = join(Page, Ref,
# 				Page.page_id == Ref.page_id)  # r = session.query(title).join(Album).filter(Album.id == 10).count()
# query = select([Page.title, Page.timeedit]).select_from(join_obj)  # .where(Page.page_id==2)
# r = session.execute(query).fetchall()
# print(r)



# query = session.query(Page.title).outerjoin(WarningTps).filter(
# 	WarningTps.page_id == None)  # Page.page_id == Ref.page_id
# r = session.execute(query).fetchall()
# print(r)  # engine = create_engine('sqlite:///:memory:', echo=True)

query = session.query(Page)  # Page.page_id == Ref.page_id
r = session.execute(query).fetchall()
print(r)  # engine = create_engine('sqlite:///:memory:', echo=True)

# metadata = MetaData()
#
# users_table = Table('users', metadata,
# 					Column('id', Integer, primary_key=True),
# 					Column('name', String),
# 					Column('fullname', String),
# 					Column('password', String)
# 					)
#
# metadata.create_all(engine)
#
#
# class User(object):
# 	def __init__(self, name, fullname, password):
# 		self.name = name
# 		self.fullname = fullname
# 		self.password = password
#
# 	def __repr__(self):
# 		return "<User('%s','%s', '%s')>" % (self.name, self.fullname, self.password)
#
#
# from sqlalchemy.orm import mapper  # достать "Отобразитель" из пакета с объектно-реляционной моделью
#
# print(mapper(User, users_table))  # и отобразить. Передает класс User и нашу таблицу
# user = User("Вася", "Василий", "qweasdzxc")
# print(user)  # Напечатает <User('Вася', 'Василий', 'qweasdzxc'>
# print(user.id)  # Напечатает None

from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base  # session = sessionmaker(bind=engine)





# db_engine = create_engine('sqlite:///:memory:', echo=True)
# # создадём таблицы
# metadata.create_all(db_engine)
# # начинаем новую сессию работы с БД
# Session = sessionmaker(bind=db_engine)
# session = Session()

# Base = declarative_base()
# class Page(Base):
# 	__tablename__ = 'pages'
# 	page_id = Column('page_id', Integer, primary_key=True)
# 	title = Column('title', String)
# 	timeedit = Column('timeedit', Integer)
#
# 	def __init__(self, title, page_id, timeedit):
# 		self.page_id = page_id
# 		self.title = title
# 		self.timeedit = timeedit
#
#
# class Ref(Base):
# 	__tablename__ = 'refs'
# 	id = Column('id', Integer, primary_key=True)
# 	page_id = Column('page_id', String)
# 	citeref = Column('citeref', String)
# 	link_to_sfn = Column('link_to_sfn', String)
# 	text = Column('text', String)
#
# 	def __init__(self, page_id, citeref, link_to_sfn, text):
# 		self.page_id = page_id
# 		self.citeref = citeref
# 		self.link_to_sfn = link_to_sfn
# 		self.text = text



# import os
#
# if os.path.exists("some.db"):
#     os.remove("some.db")
# e = create_engine("sqlite:///some.db")
# e.execute("""
#     create table employee (
#         emp_id integer primary key,
#         emp_name varchar
#     )
# """)
# e.execute("""
#     create table employee_of_month (
#         emp_id integer primary key,
#         emp_name varchar
#     )
# """)
# e.execute("""insert into employee(emp_name) values ('ed')""")
# e.execute("""insert into employee(emp_name) values ('jack')""")
# e.execute("""insert into employee(emp_name) values ('fred')""")
