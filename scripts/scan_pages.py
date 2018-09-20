#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import time
from urllib.parse import quote

import requests
from scripts.db_models import db_session, PageWithSfn, ErrRef, Timecheck
from scripts.scan_refs_of_page import ScanRefsOfPage


def do_scan():
    """Сканирование страниц на ошибки"""
    limit = 100
    pages = db_get_list_changed_pages(limit)
    s = open_requests_session()
    while pages:
        for pid, title in pages:
            # if pid != 3690723:  continue  # For tests
            print(title)
            r = s.get(f'https://ru.wikipedia.org/wiki/{quote(title)}')
            scan_results = ScanRefsOfPage(r.text)
            db_update_pagedata(pid, scan_results.err_refs)
        pages = db_get_list_changed_pages(limit)
    s.close()


def db_update_pagedata(page_id, err_refs):
    """Сохранение результатов сканирования в БД
    Очистка db от спискастарых ошибок в поддтаблицах автоматическая, с помощью ForeignKey ondelete='CASCADE'
    """
    db_session.rollback()
    db_session.query(ErrRef).filter(ErrRef.page_id == page_id).delete()
    for ref in err_refs:
        db_session.add(ErrRef(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
    db_session.merge(Timecheck(page_id, time_current()))  # merge
    db_session.commit()


def db_get_list_changed_pages(limit=None, offset=None):
    pages = db_session.query(PageWithSfn.page_id, PageWithSfn.title) \
        .outerjoin(Timecheck, PageWithSfn.page_id == Timecheck.page_id) \
        .filter((Timecheck.timecheck.is_(None)) | (PageWithSfn.timelastedit > Timecheck.timecheck)) \
        .limit(limit).offset(offset) \
        .all()
    return pages


def open_requests_session():
    s = requests.Session()
    s.headers.update({'User-Agent': 'user:textworkerBot'})
    s.params.update({"action": "render"})
    return s


def time_current():
    return time.strftime('%Y%m%d%H%M%S', time.gmtime())

# for test
# page = ScanRefsOfPage('2091672', 'Марк Фульвий Флакк (консул 125 года до н. э.)')
# pass
