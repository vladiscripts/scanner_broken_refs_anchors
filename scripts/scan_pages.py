#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import time
from urllib.parse import quote

import requests
from scripts.db_init import db_session, SfnPageChanged, ErrRef, Timecheck
from scripts.scan_refs_of_page import ScanRefsOfPage


def do_scan():
    """Сканирование страниц на ошибки"""
    s = open_requests_session()
    pages = db_get_list_pages_for_scan()
    for id, title in pages:
        # if id != 273920:	continue  # For tests
        scan_results = scan_page(s, title)
        db_save_results(id, scan_results.err_refs)
    s.close()


def scan_page(s, title):
    """Сканирование страниц на ошибки"""
    print(f'title: {title}')
    r = s.get(f'https://ru.wikipedia.org/wiki/{quote(title)}')
    scan_results = ScanRefsOfPage(r.text)
    return scan_results


def db_save_results(page_id, err_refs):
    """Сохранение результатов сканирования в БД"""
    db_session.rollback()

    # Очистка db от списка старых ошибок
    db_session.query(ErrRef).filter(ErrRef.page_id == page_id).delete()
    db_session.query(Timecheck).filter(Timecheck.page_id == page_id).delete()

    for ref in err_refs:
        db_session.add(ErrRef(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))

    time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
    db_session.add(Timecheck(page_id, time_current))
    db_session.commit()


def db_get_list_pages_for_scan():
    pages = db_session.query(SfnPageChanged.page_id, SfnPageChanged.title) \
        .outerjoin(Timecheck, SfnPageChanged.page_id == Timecheck.page_id) \
        .filter((Timecheck.timecheck.is_(None)) | (SfnPageChanged.timelastedit > Timecheck.timecheck)).all()
    return pages


def open_requests_session():
    s = requests.Session()
    s.headers.update({'User-Agent': 'user:textworkerBot'})
    s.params.update({"action": "render"})
    return s

# for test
# page = ScanRefsOfPage('2091672', 'Марк Фульвий Флакк (консул 125 года до н. э.)')
# pass
