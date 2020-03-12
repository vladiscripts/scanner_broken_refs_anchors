#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import time
from urllib.parse import quote
import requests
import json
import pymysql.err
from scripts.db_models import PageWithSfn, ErrRef, Timecheck, Session
from scripts.scan_refs_of_page import ScanRefsOfPage
from scripts import *
from settings import *


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
            pages = db_get_list_changed_pages(limit)
            if not pages: break

            results = []
            for pid, title in pages:
                # if pid != 54229: continue
                err_refs = self.scan_page(title, pid)
                if err_refs is None:
                    continue
                # results.append([pid, err_refs])
                results.append([title, pid, err_refs])
                # else: print()

            for title, pid, err_refs in results:
                # if title == 'Скачок_Резеля': logger.info(title)
                # if pid != 54229: print()
                # if pid != 54229: continue
                db_update_pagedata(title, pid, err_refs)
            # offset = offset + limit
        self.s.close()

    def scan_page(self, title: str, pid=None) -> Optional[List[namedtuple]]:
        """Сканирование страниц на ошибки"""
        assert not (title is None or title.strip() == '')
        # logger.info(f'scan: {title}')
        try:
            if pid:
                r = self.s.get('https://ru.wikipedia.org/w/api.php', params={'pageid': pid}, timeout=60)
            else:
                r = self.s.get('https://ru.wikipedia.org/w/api.php', params={'page': title}, timeout=60)
        except Exception as e:
            # ReadTimeoutError
            logger.warning(f'{e}. pid={pid}, title={title}, error: {j["error"]}')
            return
        if r.status_code != 200:
            logger.error(f'HTTPerror {r.status_code} ({r.reason}): {title}')
        if len(r.text) < 200:
            logger.error(f'error: len(r.text) < 200 in page: {title}')
        j = json.loads(r.text)
        if 'error' in j:
            if j["error"]['code'] == 'nosuchpageid':
                logger.warning(f'on page with ID. pid={pid}, title={title}, error: {j["error"]}')
                return
            if j["error"]['code'] == 'missingtitle':
                logger.warning(f'error on page request - no page. pid={pid}, title={title}, error: {j["error"]}')
                return
        if 'error' in j or 'warnings' in j:
            logger.warning(f'error on page request. pid={pid}, title={title}, error: {j["error"]}\n')
            return
        if not 'parse' in j:
            logger.warning(f"not 'parse' in j. pid={pid}, title={title}, error: {j['error']}\n")
            return
        text = j['parse']['text']
        err_refs = ScanRefsOfPage(text)
        assert err_refs is not None
        return err_refs

    # def _scan_page_via_html(self, pid, title: str) -> Optional[List[namedtuple]]:
    #     """Сканирование страниц на ошибки"""
    #     assert not (title is None or title.strip() == '')
    #     logger.info(f'scan: {title}')
    #     # r = self.s.get(f'https://ru.wikipedia.org/wiki/{quote(title)}', timeout=60)   # + params={"action": "render"}
    #     try:
    #         r = s.get(f'https://ru.wikipedia.org/wiki/{quote(title)}')
    #     except Exception as e:
    #         logger.info(f'error: requests: {title}; {e}')
    #         return None
    #     if '|' in title:
    #         logger.debug("'|' in title: {title}")
    #     if r.status_code != 200:
    #         logger.error(f'HTTPerror {r.status_code} ({r.reason}): {title}')
    #     if len(r.text) < 200:
    #         logger.error(f'error: len(r.text) < 200 in page: {title}')
    #     err_refs = ScanRefsOfPage(r.text)
    #     assert err_refs is not None
    #     return err_refs

    def open_requests_session(self) -> requests.Session:
        s = requests.Session()
        s.headers.update({'User-Agent': 'user:textworkerBot',
                          'Accept-Encoding': 'gzip, deflate'})
        s.params.update({"action": "parse", 'format': 'json', 'prop': 'text', 'utf8': 1, 'formatversion': 2})
        # s.params.update({"action": "render"})  # для запросов как html, а не через api
        return s

    def recheck_lists(self):
        # todo: pid
        lst = file_readlines(filename_listpages_errref_where_no_yet_warning_tpl)
        lst_new = []
        for title in lst:
            # if title != 'Битва_при_Мьяхадосе':
            #     continue
            err_refs = self.scan_page(title)
            if err_refs is None:
                continue
            if len(err_refs) == 0:
                logger.error(f'no errrefs on page "{title}", where it should be')
                continue
            lst_new.append(title)
        file_savelines(filename_listpages_errref_where_no_yet_warning_tpl, lst_new)

        lst = file_readlines(filename_list_to_remove_warning_tpl)
        lst_new = []
        for title in lst:
            err_refs = self.scan_page(title)
            if err_refs is None:
                continue
            if len(err_refs) > 0:
                logger.error(f'errrefs on page "{title}", where it should not be')
                continue
            lst_new.append(title)
        file_savelines(filename_list_to_remove_warning_tpl, lst_new)


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


def db_update_pagedata_(s, title: str, page_id: int, err_refs: list, chktime: str) -> None:
    """Сохранение результатов сканирования в БД
    Очистка db от списка старых ошибок в поддтаблицах автоматическая, с помощью ForeignKey ondelete='CASCADE'
    """
    try:
        with s.begin_nested():
            s.query(ErrRef).filter(ErrRef.page_id == page_id).delete()
            for ref in err_refs:
                s.add(ErrRef(page_id, ref.citeref, ref.link_to_sfn, ref.text))
            s.merge(Timecheck(page_id, chktime))
        s.commit()
        # s.begin_nested()
        # s.query(ErrRef).filter(ErrRef.page_id == page_id).delete()
        # for ref in err_refs:
        #     s.add(ErrRef(page_id, ref.citeref, ref.link_to_sfn, ref.text))
        # s.merge(Timecheck(page_id, chktime))
        # s.commit()
    except pymysql.err.DataError as e:
        if len(ref.citeref) > 255 or len(ref.text) > 255:
            print()
        print()
    except Exception as e:
        print()


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
