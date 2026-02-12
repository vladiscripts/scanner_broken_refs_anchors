#!/usr/bin/env python
# author: https://github.com/vladiscripts
import time
from typing import NamedTuple
from scripts.db_models import PagesWithSfn, ErrRef, Timecheck, Session
from scripts.scan_refs_of_page import ScanRefsOfPage, SFN
from scripts import datetime, timezone, logger
from . import request_html


# [p.page_id for p in Session.query(PageWithSfn.page_id, PageWithSfn.title) \
#         .outerjoin(Timecheck, PageWithSfn.page_id == Timecheck.page_id) \
#         .filter((Timecheck.timecheck.is_(None)) | (PageWithSfn.timelastedit > Timecheck.timecheck)) \
#         .all()]

class PageData(NamedTuple):
    title: str
    pid: int  # page_id
    err_refs: list[SFN]


class Scanner:
    def __init__(self):
        self.pages_limit_by_query = 300
        self.downloader = request_html.Downloader()

    def do_scan(self):
        """Сканирование страниц на ошибки"""
        while True:
            pages = db_get_list_changed_pages(limit=self.pages_limit_by_query)
            if not pages:
                break
            results = []
            for pid, title in pages:
                logger.info(f'scan: {title}')
                if err_refs := self.scan_page(title, pid):
                    results.append(PageData(title, pid, err_refs))

            for p in results:
                # if title == 'Скачок_Резеля': logger.info(title)
                # if pid != 54229: print()
                db_update_pagedata(p, datetime.now(timezone.utc))
        self.downloader.s.close()

    def scan_page(self, title: str, pid=None) -> list[SFN] | None:
        """Сканирование страниц на ошибки"""
        if text := self.downloader.get_page(title, pid):
            err_refs = ScanRefsOfPage(text)
            return err_refs


def db_get_list_changed_pages(limit=None) -> list[tuple[int, str]]:
    with Session() as s:
        q = s.query(PagesWithSfn).outerjoin(Timecheck, PagesWithSfn.page_id == Timecheck.page_id) \
            .filter((Timecheck.timecheck.is_(None)) | (PagesWithSfn.timelastedit > Timecheck.timecheck))
        if limit:
            q = q.limit(limit)
        _pages = q.all()
        pages = [(p.page_id, p.title) for p in _pages]
        return pages


def db_delete_page_id(pid: int):
    with Session() as s:
        s.query(PagesWithSfn).filter(PagesWithSfn.page_id == pid).delete(synchronize_session='fetch')
        s.commit()


def db_update_pagedata_(s, p: PageData, chktime: datetime) -> None:
    """Сохранение результатов сканирования в БД
    Очистка db от списка старых ошибок в поддтаблицах автоматическая, с помощью ForeignKey ondelete='CASCADE'
    """
    with s.begin_nested():
        s.query(ErrRef).filter(ErrRef.page_id == p.pid).delete(synchronize_session='fetch')
        for ref in p.err_refs:
            s.add(ErrRef(p.pid, ref.citeref, ref.link_to_sfn, ref.text))
        s.merge(Timecheck(p.pid, chktime))
    s.commit()


def db_update_pagedata(p: PageData, chktime: datetime) -> None:
    """Сохранение результатов сканирования в БД"""
    logger.debug(f'db_updating: {p.title}')
    with Session() as s:
        db_update_pagedata_(s, p, chktime)
    logger.debug(f'db_updated: {p.title}')


# @staticmethod
# def db_update_pagedata_packet(pages: List[Tuple[str, int, tuple]]) -> None:
#     """Сохранение результатов сканирования в БД
#     Очистка db от списка старых ошибок в поддтаблицах автоматическая, с помощью ForeignKey ondelete='CASCADE'
#     """
#     with Session() as s:
#         pids = [pid for title, pid, err_refs in pages]
#         s.query(ErrRef).filter(ErrRef.page_id.in_(pids)).delete(synchronize_session='fetch')
#         for title, pid, err_refs in pages:
#             for ref in err_refs:
#                 s.add(ErrRef(pid, ref.citeref, ref.link_to_sfn, ref.text))
#             s.merge(Timecheck(pid, time_current()))
#         s.commit()


def time_current():
    return time.strftime('%Y%m%d%H%M%S', time.gmtime())
    # return datetime.timestamp()..utcfromtimestamp(ts).strftime('%Y%m%d%H%M%S')

# for test
# page = ScanRefsOfPage('2091672', 'Марк Фульвий Флакк (консул 125 года до н. э.)')
# pass
