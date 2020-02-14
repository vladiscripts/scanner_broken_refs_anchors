#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import time
from urllib.parse import quote
import requests
from scripts.__init__ import *
from scripts.db_models import PageWithSfn, ErrRef, Timecheck, Session
from scripts.scan_refs_of_page import ScanRefsOfPage


# [p.page_id for p in Session.query(PageWithSfn.page_id, PageWithSfn.title) \
#         .outerjoin(Timecheck, PageWithSfn.page_id == Timecheck.page_id) \
#         .filter((Timecheck.timecheck.is_(None)) | (PageWithSfn.timelastedit > Timecheck.timecheck)) \
#         .all()]


class Scanner:
    def __init__(self):
        self.s = self.open_requests_session()

    def do_scan(self):
        """Сканирование страниц на ошибки"""
        offset, limit = 0, 100
        # s = open_requests_session()
        while True:
            # pages = self.db_get_list_changed_pages(offset, limit)
            pages = self.db_get_list_changed_pages(limit)
            if not pages: break

            results = []
            for pid, title in pages:
                # if pid != 54229: continue
                err_refs = self.scan_page(title)
                # results.append([pid, err_refs])
                if err_refs is not None:
                    results.append([pid, err_refs])
                # else: print()

            for pid, err_refs in results:
                # if title == 'Скачок_Резеля': logging.info(title)
                # if pid != 54229: print()
                # if pid != 54229: continue
                self.db_update_pagedata(pid, err_refs)
            # offset = offset + limit

        self.s.close()

    def scan_page(self, title):
        """Сканирование страниц на ошибки"""
        logging.info(title)
        if not title or title == '':
            return
        r = self.s.get(f'https://ru.wikipedia.org/wiki/{quote(title)}')
        # try:
        #     r = s.get(f'https://ru.wikipedia.org/wiki/{quote(title)}')
        # except Exception as e:
        #     logging.info(f'error: requests: {title}; {e}')
        #     return None
        if r.status_code != 200:
            logging.error(f'error: r.status_code != 200: {title}')
        if len(r.text) < 200:
            logging.error(f'error: len(r.text) < 200 in page: {title}')
        err_refs = ScanRefsOfPage(r.text)
        return err_refs

    def open_requests_session(self):
        s = requests.Session()
        s.headers.update({'User-Agent': 'user:textworkerBot'})
        s.params.update({"action": "render"})
        return s

    @staticmethod
    def db_get_list_changed_pages(limit):  # offset,limit
        Session()
        pages = Session.query(PageWithSfn.page_id, PageWithSfn.title) \
            .outerjoin(Timecheck, PageWithSfn.page_id == Timecheck.page_id) \
            .filter((Timecheck.timecheck.is_(None)) | (PageWithSfn.timelastedit > Timecheck.timecheck)) \
            .limit(limit)
        # .all()
        # .offset(offset).limit(limit).all()
        Session.remove()
        return pages

    @staticmethod
    def db_update_pagedata(page_id, err_refs):
        """Сохранение результатов сканирования в БД
        Очистка db от спискастарых ошибок в поддтаблицах автоматическая, с помощью ForeignKey ondelete='CASCADE'
        """
        # todo: В БД пишется моё время или UTC?
        Session()
        # Session.rollback()
        Session.query(ErrRef).filter(ErrRef.page_id == page_id).delete()
        for ref in err_refs:
            Session.add(ErrRef(page_id, ref.citeref, ref.link_to_sfn, ref.text))
        Session.merge(Timecheck(page_id, time_current()))  # merge
        Session.commit()
        Session.remove()


def time_current():
    return time.strftime('%Y%m%d%H%M%S', time.gmtime())

# for test
# page = ScanRefsOfPage('2091672', 'Марк Фульвий Флакк (консул 125 года до н. э.)')
# pass
