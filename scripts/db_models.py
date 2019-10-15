# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session
import re
from urllib.parse import quote_from_bytes, unquote

# Для создания таблицы надо Base = declarative_base() и ...create_all() внизу под классами
# https://ru.wikibooks.org/wiki/SQLAlchemy
db_engine = create_engine('sqlite:///pagesrefs.sqlite', echo=False)  # 'sqlite:///:memory:'
Base = declarative_base()
Session = scoped_session(sessionmaker(bind=db_engine))


# Session = sessionmaker(bind=db_engine)
# db_session = Session()

# db_engine_mysql = create_engine('mysql+pymysql://v:v@localhost/wikirefsDB', echo=print_log)
# Session_mysql = sessionmaker(bind=db_engine_mysql)
# db_session_mysql = Session_mysql()


class PageWithSfn(Base):
    """Страницы с шаблоном типа {{sfn}}"""
    __tablename__ = 'pages_with_sfn'
    page_id = Column(Integer, primary_key=True)
    title = Column(String, unique=True, nullable=False)
    timelastedit = Column(Integer)
    wikilist = Column(String, index=True)
    timechecks = relationship('Timecheck', backref='page', passive_deletes=True)  # cascade='all,delete,delete-orphan'
    refs = relationship('ErrRef', backref='page', passive_deletes=True)

    def __init__(self, page_id, title, timelastedit):
        self.page_id = page_id
        self.title = byte2utf(title)
        self.timelastedit = timelastedit
        fl = self.title[0:1].upper()
        self.wikilist = fl if re.match(r'[А-ЯЁ]', fl) else '*'


class Timecheck(Base):
    """Время проверки страниц скриптом"""
    __tablename__ = 'timecheck'
    page_id = Column(Integer, ForeignKey('pages_with_sfn.page_id', ondelete='CASCADE'), primary_key=True)
    timecheck = Column(Integer)

    def __init__(self, page_id, timecheck):
        self.page_id = page_id
        self.timecheck = timecheck


class ErrRef(Base):
    """Списки ошибочных сносок страниц"""
    __tablename__ = 'erroneous_refs'
    id = Column(Integer, primary_key=True)
    page_id = Column(Integer, ForeignKey('pages_with_sfn.page_id', ondelete='CASCADE'), index=True)
    citeref = Column(String)
    link_to_sfn = Column(String)
    text = Column(String)

    def __init__(self, page_id, citeref, link_to_sfn, text):
        self.page_id = page_id
        self.citeref = citeref
        self.link_to_sfn = link_to_sfn
        self.text = text


class PageWithWarning(Base):
    """Страницы с шаблоном об ошибке сносок"""
    __tablename__ = 'pages_with_warnings'
    page_id = Column(Integer, primary_key=True)
    title = Column(String, unique=True)

    def __init__(self, page_id, title):
        self.page_id = page_id
        self.title = byte2utf(title)


class Wikilists(Base):
    """Названия подстраниц бота со списками ошибок"""
    __tablename__ = 'wikilists'
    letter = Column(String, ForeignKey('pages_with_sfn.wikilist'), primary_key=True)
    title = Column(String)

    def __init__(self, letter, title):
        self.letter = letter
        self.title = title


def byte2utf(string):
    return unquote(quote_from_bytes(string), encoding='utf8')


Base.metadata.create_all(db_engine)
