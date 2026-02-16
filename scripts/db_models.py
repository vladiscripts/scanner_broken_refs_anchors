from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base, validates
from datetime import datetime

from engine_conn_str import engine_conn_str

# from sqlalchemy.engine.url import URL
# myDB = URL(drivername='mysql+pymysql', host='localhost', database='',
#            query={'read_default_file': '~/.pywikibot/replica.my.cnf'})
# engine = create_engine(name_or_url=myDB)
db_engine = create_engine(engine_conn_str, echo=False, pool_pre_ping=True)
Session = sessionmaker(bind=db_engine)
Base = declarative_base()


class BaseModel:
    def as_dict(self) -> dict[str, str]:
        return {col.key: getattr(self, col.key) for col in inspect(self.__class__).columns if col.key != 'id'}


class PagesWithSfn(BaseModel, Base):
    """Страницы с шаблоном типа {{sfn}}"""
    __tablename__ = 'pages_with_sfn'
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
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


class Timecheck(BaseModel, Base):
    """Время проверки страниц скриптом"""
    __tablename__ = 'timecheck'
    page_id = Column(Integer, ForeignKey('pages_with_sfn.page_id', ondelete='CASCADE', onupdate='CASCADE'), primary_key=True)
    timecheck = Column(DateTime)


class ErrRef(BaseModel, Base):
    """Списки ошибочных сносок страниц"""
    __tablename__ = 'erroneous_refs'
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    id = Column(Integer, primary_key=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey('pages_with_sfn.page_id', ondelete='CASCADE', onupdate='CASCADE'), index=True)
    citeref = Column(String(255), nullable=False)
    link_to_sfn = Column(String(2000), nullable=False)
    text = Column(String(255), nullable=False)

    def __init__(self, page_id: int, citeref: str, link_to_sfn: str, text: str):
        self.page_id = page_id
        self.citeref = citeref
        self.link_to_sfn = link_to_sfn
        self.text = text

    @validates('citeref', 'text')
    def validate_length(self, key, value):
        max_len = self.__table__.c[key].type.length
        if value and len(value) > max_len:
            return value[:max_len]
        return value


class PageWithWarning(BaseModel, Base):
    """Страницы с шаблоном об ошибке сносок"""
    __tablename__ = 'pages_with_warnings'
    __table_args__ = {'mysql_charset': 'utf8mb4', 'mysql_collate': 'utf8mb4_unicode_ci'}
    page_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)

    def __init__(self, page_id, title):
        self.page_id = page_id
        self.title = title


Base.metadata.create_all(bind=db_engine)
