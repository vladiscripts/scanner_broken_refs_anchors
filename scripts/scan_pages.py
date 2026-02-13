#!/usr/bin/env python
# author: https://github.com/vladiscripts
import time
from typing import NamedTuple
from sqlalchemy import select, delete
from sqlalchemy.dialects.mysql import insert
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
    checktime: datetime


class Scanner:
    def __init__(self):
        self.pages_limit_by_query = 300
        self.downloader = request_html.Downloader()

    def do_scan(self):
        """Сканирование страниц на ошибки"""
        while True:
            pages = db_get_list_changed_pages(limit=self.pages_limit_by_query)
            logger.info(f'Сканируем пачку из {len(pages)} изменённых страниц...')
            if not pages:
                break
            results = []
            for pid, title in pages:
                logger.info(f'scan: {title}')
                err_refs = self.scan_page(title, pid)
                if err_refs is None:
                    logger.debug(f'Ошибка при скачивании страницы "{title}", {pid=}')
                    continue
                p = PageData(title, pid, err_refs, datetime.now(timezone.utc))
                results.append(p)

            db_update_pages_data(results)

        self.downloader.s.close()

    def scan_page(self, title: str, pid: int) -> list[SFN] | None:
        """Сканирование страницы на ошибки"""
        if text := self.downloader.get_page(title, pid):
            return ScanRefsOfPage(text)
        return None


def db_get_list_changed_pages(limit=None) -> list[tuple[int, str]]:
    """ Возвращает страницы, которые ещё не проверялись (timecheck IS NULL), или изменились с последней проверки (timelastedit > timecheck)"""
    with Session() as s:
        stmt = (
            select(PagesWithSfn.page_id, PagesWithSfn.title)
            .outerjoin(Timecheck, PagesWithSfn.page_id == Timecheck.page_id)
            .where(
                (Timecheck.timecheck.is_(None)) |
                (PagesWithSfn.timelastedit > Timecheck.timecheck))
            .order_by(PagesWithSfn.page_id))
        if limit:
            stmt = stmt.limit(limit)
        r = s.execute(stmt)
        records = [(p.page_id, p.title) for p in r]
        return records


def db_delete_page_id(pid: int):
    with Session() as s:
        stmt = delete(PagesWithSfn).where(PagesWithSfn.page_id == pid)
        s.execute(stmt)
        s.commit()


# def db_update_pagedata_(s, p: PageData) -> None:
#     """Сохранение результатов сканирования в БД
#     Очистка db от списка старых ошибок в поддтаблицах автоматическая, с помощью ForeignKey ondelete='CASCADE'
#     """
#     with s.begin_nested():
#         s.query(ErrRef).filter(ErrRef.page_id == p.pid).delete(synchronize_session='fetch')
#         for ref in p.err_refs:
#             s.add(ErrRef(p.pid, ref.citeref, ref.link_to_sfn, ref.text))
#         s.merge(Timecheck(p.pid, p.checktime))


def db_update_pages_data(pages: list[PageData]) -> None:
    """Сохранение результатов сканирования в БД"""
    logger.debug(f'db_updating')
    try:
        with Session() as s:
            for p in pages:
                # Удалить записи из таблицы о битых сносках
                s.execute(delete(ErrRef).where(ErrRef.page_id == p.pid))

                # Обновить таблицу с битыми сносками
                if p.err_refs:
                    err_objects = [ErrRef(p.pid, ref.citeref, ref.link_to_sfn, ref.text) for ref in p.err_refs]
                    err_data = [obj.as_dict() for obj in err_objects]
                    s.execute(insert(ErrRef), err_data)

                # Обновить таблицу с датой последнего сканирования
                stmt = (insert(Timecheck.__table__).values(page_id=p.pid, timecheck=p.checktime).on_duplicate_key_update(timecheck=p.checktime))
                s.execute(stmt)
            s.commit()
            logger.debug('Пакет обновлён в БД')

    except Exception as e:
        logger.error(f"Ошибка при обновлении БД: {e}")
        raise

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


# for test
# page = ScanRefsOfPage('2091672', 'Марк Фульвий Флакк (консул 125 года до н. э.)')
# pass
