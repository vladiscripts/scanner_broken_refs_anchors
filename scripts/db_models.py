from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import datetime

from engine_conn_str import engine_conn_str

# from sqlalchemy.engine.url import URL
# myDB = URL(drivername='mysql+pymysql', host='localhost', database='',
#            query={'read_default_file': '~/.pywikibot/replica.my.cnf'})
# engine = create_engine(name_or_url=myDB)
db_engine = create_engine(engine_conn_str, echo=False)
Session = sessionmaker(bind=db_engine)
Base = declarative_base()


class PagesWithSfn(Base):
    """Страницы с шаблоном типа {{sfn}}"""
    __tablename__ = 'pages_with_sfn'
    page_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    timelastedit = Column(DateTime)  # VARBINARY(14) on wikiDB

    # ref = relationship('ErrRef', backref='refs', passive_deletes=True)
    # timecheck = relationship('Timecheck', backref='timechecks',
    #                          passive_deletes=True)  # cascade='all,delete,delete-orphan'
    # ref = relationship('ErrRef', backref='refs', passive_deletes=True)

    def __init__(self, page_id, title, timelastedit: datetime):
        self.page_id = page_id
        self.title = title
        self.timelastedit = timelastedit


class Timecheck(Base):
    """Время проверки страниц скриптом"""
    __tablename__ = 'timecheck'
    page_id = Column(Integer, ForeignKey('pages_with_sfn.page_id', ondelete='CASCADE', onupdate='CASCADE'),
                     primary_key=True)
    timecheck = Column(DateTime)

    def __init__(self, page_id, timecheck: datetime):
        self.page_id = page_id
        self.timecheck = timecheck


class ErrRef(Base):
    """Списки ошибочных сносок страниц"""
    __tablename__ = 'erroneous_refs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey('pages_with_sfn.page_id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    citeref = Column(String(255), nullable=False)
    link_to_sfn = Column(String(2000), nullable=False)
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
        self.title = title


Base.metadata.create_all(bind=db_engine)
