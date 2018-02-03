# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey
import re
from config import *

Base = declarative_base()
db_engine = create_engine('sqlite:///pagesrefs.sqlite', echo=print_log)  # 'sqlite:///:memory:'
Base.metadata.create_all(db_engine)
Session = sessionmaker(bind=db_engine)
db_session = Session()


# Объявление таблиц --------------
# должно быть ниже объявления Base

class Page(Base):
	__tablename__ = 'pages'
	page_id = Column(Integer, primary_key=True, unique=True)
	title = Column(String, unique=True)
	timeedit = Column(Integer)
	wikilist = Column(String, index=True)

	def __init__(self, page_id, title, timeedit):
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
	__tablename__ = 'erroneous_refs'
	id = Column(Integer, primary_key=True)
	page_id = Column(Integer, ForeignKey('pages.page_id'), index=True)
	citeref = Column(String)
	link_to_sfn = Column(String)
	text = Column(String)

	def __init__(self, page_id, citeref, link_to_sfn, text):
		self.page_id = page_id
		self.citeref = citeref
		self.link_to_sfn = link_to_sfn
		self.text = text


class WarningTpls(Base):
	__tablename__ = 'warnings'
	page_id = Column(Integer, ForeignKey('pages.page_id'), ForeignKey('erroneous_refs.page_id'), primary_key=True, unique=True)
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


# Helpers
def queryDB(query):
	return db_session.execute(query).fetchall()
