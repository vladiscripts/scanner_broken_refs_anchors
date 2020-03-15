# -*- coding: utf-8 -*-
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, scoped_session, Query
import re
from urllib.parse import quote_from_bytes, unquote
from datetime import datetime
from engine_conn_str import engine_conn_str

# from sqlalchemy.engine.url import URL
# myDB = URL(drivername='mysql+pymysql', host='localhost', database='',
#            query={'read_default_file': '~/.pywikibot/replica.my.cnf'})
# engine = create_engine(name_or_url=myDB)
db_engine = create_engine(engine_conn_str, echo=True)

Session = sessionmaker(bind=db_engine)
db_session = Session()

Base = declarative_base(bind=db_engine)


class PageWithSfn(Base):
    """Страницы с шаблоном типа {{sfn}}"""
    __tablename__ = 'pages_with_sfn'
    page_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    timelastedit = Column(DateTime)  # VARBINARY(14) on wikiDB
    wikilist = Column(String(3), index=True)

    # wikilist = Column(String(3), ForeignKey('pages_with_sfn.wikilist'), primary_key=True, index=True)
    # wikilist = Column(String(3), ForeignKey('wikilists.letter'))
    # wikilist = relationship('Wikilists', backref='ww', passive_deletes=True)
    # ref = relationship('ErrRef', backref='refs', passive_deletes=True)
    # timecheck = relationship('Timecheck', backref='timechecks',
    #                          passive_deletes=True)  # cascade='all,delete,delete-orphan'
    # ref = relationship('ErrRef', backref='refs', passive_deletes=True)

    def __init__(self, page_id, title, timelastedit):
        self.page_id = page_id
        self.title = byte2utf(title)
        self.timelastedit = datetime.strptime(timelastedit.decode(), '%Y%m%d%H%M%S')
        fl = self.title[0:1].upper()
        if fl == 'Ё': fl = 'Е'
        self.wikilist = fl if re.match(r'[А-ЯЁ]', fl) else '*'


class Timecheck(Base):
    """Время проверки страниц скриптом"""
    __tablename__ = 'timecheck'
    page_id = Column(Integer, ForeignKey('pages_with_sfn.page_id', ondelete='CASCADE', onupdate='CASCADE'),
                     primary_key=True)
    timecheck = Column(DateTime)

    def __init__(self, page_id, timecheck):
        self.page_id = page_id
        self.timecheck = timecheck


class ErrRef(Base):
    """Списки ошибочных сносок страниц"""
    __tablename__ = 'erroneous_refs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey('pages_with_sfn.page_id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    citeref = Column(String(255), nullable=False)
    link_to_sfn = Column(String(255), nullable=False)
    text = Column(String(255), nullable=False)

    def __init__(self, page_id, citeref, link_to_sfn, text):
        self.page_id = page_id
        self.citeref = citeref[:255]
        self.link_to_sfn = link_to_sfn
        self.text = text[:255]


class PageWithWarning(Base):
    """Страницы с шаблоном об ошибке сносок"""
    __tablename__ = 'pages_with_warnings'
    page_id = Column(Integer, primary_key=True)
    title = Column(String(255), unique=True, nullable=False)

    def __init__(self, page_id, title):
        self.page_id = page_id
        self.title = byte2utf(title)


class Wikilists(Base):
    """Названия подстраниц бота со списками ошибок"""
    __tablename__ = 'wikilists'
    # id = Column(Integer, primary_key=True, autoincrement=True)
    # letter = Column(String(3), unique=True)
    letter = Column(String(3), primary_key=True, autoincrement=False)
    title = Column(String(255), nullable=False)

    # pages = relationship('PageWithSfn', backref='wikilist', passive_deletes=True)
    # pages = relationship('PageWithSfn', backref='pages', passive_deletes=True)

    def __init__(self, letter, title):
        self.letter = letter
        self.title = title


def byte2utf(string):
    return unquote(quote_from_bytes(string), encoding='utf8')


def create_tables():
    def make_wikilist_titles():
        wikilists = (
            ('А', 'А'), ('Б', 'Б'), ('В', 'ВГ'), ('Г', 'ВГ'), ('Д', 'Д'),
            ('Е', 'ЕЁЖЗИЙ'), ('Ё', 'ЕЁЖЗИЙ'), ('Ж', 'ЕЁЖЗИЙ'), ('З', 'ЕЁЖЗИЙ'), ('И', 'ЕЁЖЗИЙ'), ('Й', 'ЕЁЖЗИЙ'),
            ('К', 'К'), ('Л', 'ЛМ'), ('М', 'ЛМ'), ('Н', 'НО'),
            ('О', 'НО'), ('П', 'П'), ('Р', 'Р'), ('С', 'С'), ('Т', 'Т'),
            ('У', 'УФХ'), ('Ф', 'УФХ'), ('Х', 'УФХ'),
            ('Ц', 'ЦЧШЩЪЫЬЭЮЯ'), ('Ч', 'ЦЧШЩЪЫЬЭЮЯ'), ('Ш', 'ЦЧШЩЪЫЬЭЮЯ'), ('Щ', 'ЦЧШЩЪЫЬЭЮЯ'), ('Ъ', 'ЦЧШЩЪЫЬЭЮЯ'),
            ('Ы', 'ЦЧШЩЪЫЬЭЮЯ'), ('Ь', 'ЦЧШЩЪЫЬЭЮЯ'), ('Э', 'ЦЧШЩЪЫЬЭЮЯ'), ('Ю', 'ЦЧШЩЪЫЬЭЮЯ'), ('Я', 'ЦЧШЩЪЫЬЭЮЯ'),
            ('*', 'Не русские буквы'),
        )
        for letter, pagename in wikilists:
            db_session.merge(Wikilists(letter, pagename))
        db_session.commit()

    Base.metadata.create_all()
    make_wikilist_titles()


create_tables()
