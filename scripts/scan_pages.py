#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import requests
import json
import pymysql.err
from scripts.db_models import PageWithSfn, ErrRef, Timecheck, Session, db_session as s
from scripts.scan_refs_of_page import ScanRefsOfPage
from scripts import *
from settings import *
from . import request_html


# [p.page_id for p in Session.query(PageWithSfn.page_id, PageWithSfn.title) \
#         .outerjoin(Timecheck, PageWithSfn.page_id == Timecheck.page_id) \
#         .filter((Timecheck.timecheck.is_(None)) | (PageWithSfn.timelastedit > Timecheck.timecheck)) \
#         .all()]


class Scanner:
    def __init__(self):
        self.pages_limit_by_query = 300
        self.downloader = request_html.Downloader()

    def do_scan(self):
        """Сканирование страниц на ошибки"""
        while True:
            pages = db_get_list_changed_pages(s, limit=self.pages_limit_by_query)
            if not pages: break
            results = []
            for pid, title in pages:
                logger.info(f'scan: {title}')
                err_refs = self.scan_page(title, pid)
                if err_refs is None:
                    continue
                results.append([title, pid, err_refs])

            for title, pid, err_refs in results:
                # if title == 'Скачок_Резеля': logger.info(title)
                # if pid != 54229: print()
                db_update_pagedata_(s, title, pid, err_refs, datetime.utcnow())
        self.downloader.s.close()

    def scan_page(self, title: str, pid=None) -> Optional[List[namedtuple]]:
        """Сканирование страниц на ошибки"""
        text = self.downloader.get_page(title, pid)
        if text is not None:
            err_refs = ScanRefsOfPage(text)
            return err_refs


def session_(func):
    def wrapper(*kargs, **kwargs):
        s = Session()
        # s.rollback()
        result = func(s, *kargs, **kwargs)
        s.remove()
        return result

    return wrapper


def db_get_list_changed_pages(s, limit=None) -> list:  # offset,limit
    # s = Session()
    if limit:
        _pages = s.query(PageWithSfn) \
            .outerjoin(Timecheck, PageWithSfn.page_id == Timecheck.page_id) \
            .filter((Timecheck.timecheck.is_(None)) | (PageWithSfn.timelastedit > Timecheck.timecheck)) \
            .limit(limit).all()
    else:
        _pages = s.query(PageWithSfn) \
            .outerjoin(Timecheck, PageWithSfn.page_id == Timecheck.page_id) \
            .filter((Timecheck.timecheck.is_(None)) | (PageWithSfn.timelastedit > Timecheck.timecheck)) \
            .all()
    # .offset(offset).limit(limit).all()
    # Session.remove()
    pages = [(p.page_id, p.title) for p in _pages]
    return pages


def db_delete_page_id(s, pid=int):
    s.query(PageWithSfn).filter(PageWithSfn.page_id == pid).delete()
    s.commit()


@session_
def db_update_pagedata__(s, title: str, page_id: int, err_refs: list) -> None:
    """Сохранение результатов сканирования в БД
    Очистка db от списка старых ошибок в поддтаблицах автоматическая, с помощью ForeignKey ondelete='CASCADE'
    """
    # todo: В БД пишется моё время или UTC?
    s.begin()
    s.query(ErrRef).filter(ErrRef.page_id == page_id).delete()
    for ref in err_refs:
        s.add(ErrRef(page_id, ref.citeref, ref.link_to_sfn, ref.text))
    s.merge(Timecheck(page_id, time_current()))
    s.commit()


def db_update_pagedata_(s, title: str, page_id: int, err_refs: list, chktime: datetime) -> None:
    """Сохранение результатов сканирования в БД
    Очистка db от списка старых ошибок в поддтаблицах автоматическая, с помощью ForeignKey ondelete='CASCADE'
    """
    # try:
    #     with s.begin_nested():
    #         s.query(ErrRef).filter(ErrRef.page_id == page_id).delete()
    #         for ref in err_refs:
    #             s.add(ErrRef(page_id, ref.citeref, ref.link_to_sfn, ref.text))
    #         s.merge(Timecheck(page_id, chktime))
    #     s.commit()
    # except pymysql.err.DataError as e:
    #     print(title)
    #     if len(ref.citeref) > 255 or len(ref.text) > 255:
    #         print('len(ref.citeref) > 255 or len(ref.text) > 255')
    #     print(e)
    # except Exception as e:
    #     print(title)
    #     print(e)
    with s.begin_nested():
        s.query(ErrRef).filter(ErrRef.page_id == page_id).delete()
        for ref in err_refs:
            s.add(ErrRef(page_id, ref.citeref, ref.link_to_sfn, ref.text))
        s.merge(Timecheck(page_id, chktime))
    s.commit()


def db_update_pagedata(title: str, page_id: int, err_refs: list) -> None:
    """Сохранение результатов сканирования в БД
    Очистка db от списка старых ошибок в поддтаблицах автоматическая, с помощью ForeignKey ondelete='CASCADE'
    """
    logger.debug(f'db_updating: {title}')
    s = Session()
    # Session.rollback()
    db_update_pagedata_(s, title, page_id, err_refs)
    # Session.remove()
    s.close()
    logger.debug(f'db_updated: {title}')


# @staticmethod
# def db_update_pagedata_packet(pages: List[Tuple[str, int, tuple]]) -> None:
#     """Сохранение результатов сканирования в БД
#     Очистка db от списка старых ошибок в поддтаблицах автоматическая, с помощью ForeignKey ondelete='CASCADE'
#     """
#     Session()
#     # Session.rollback()
#     pids = [pid for title, pid, err_refs in pages]
#     Session.query(ErrRef).filter(ErrRef.page_id.in_(pids)).delete(synchronize_session='fetch')
#     for title, pid, err_refs in pages:
#         for ref in err_refs:
#             Session.add(ErrRef(pid, ref.citeref, ref.link_to_sfn, ref.text))
#         Session.merge(Timecheck(pid, time_current()))
#     Session.commit()
#     Session.remove()


def time_current():
    return time.strftime('%Y%m%d%H%M%S', time.gmtime())
    # return datetime.timestamp()..utcfromtimestamp(ts).strftime('%Y%m%d%H%M%S')

# for test
# page = ScanRefsOfPage('2091672', 'Марк Фульвий Флакк (консул 125 года до н. э.)')
# pass
