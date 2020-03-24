#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import requests
import json
from scripts.scan_refs_of_page import ScanRefsOfPage
from scripts import *


class Downloader:
    def __init__(self):
        self.s = self.open_requests_session()

    def open_requests_session(self) -> requests.Session:
        s = requests.Session()
        s.headers.update({'User-Agent': 'user:textworkerBot',
                          'Accept-Encoding': 'gzip, deflate'})
        s.params.update({"action": "parse", 'format': 'json', 'prop': 'text', 'utf8': 1, 'formatversion': 2})
        # s.params.update({"action": "render"})  # для запросов как html, а не через api
        return s

    def get_page(self, title: str, pid=None) -> Optional[str]:
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
            logger.warning(f'{e}. pid={pid}, title={title}, error: {e}')
            return
        if r.status_code != 200:
            logger.error(f'HTTPerror {r.status_code} ({r.reason}): {title}')
        if len(r.text) < 200:
            logger.error(f'error: len(r.text) < 200 in page: {title}')
        j = json.loads(r.text)
        if 'error' in j:
            if j["error"]['code'] == 'nosuchpageid':
                logger.warning(f'on page with ID. pid={pid}, title={title}, error: {j["error"]}')
            elif j["error"]['code'] == 'missingtitle':
                logger.warning(f'error on page request - no page. pid={pid}, title={title}, error: {j["error"]}')
            else:
                logger.warning(f'error on page request. pid={pid}, title={title}, error: {j["error"]}\n')
            return
        if 'warnings' in j:
            logger.warning(f'warnings on page request. pid={pid}, title={title}, error: {j["error"]}\n')
            return
        if not 'parse' in j:
            logger.warning(f"not 'parse' in j. pid={pid}, title={title}, error: {j['error']}\n")
            return
        return j['parse']['text']

    def get_page_via_html(self, pid, title: str) -> Optional[List[namedtuple]]:
        """Сканирование страниц на ошибки"""
        from urllib.parse import quote
        assert not (title is None or title.strip() == '')
        logger.info(f'scan: {title}')
        try:
            r = self.s.get(f'https://ru.wikipedia.org/wiki/{quote(title)}', timeout=60)  # + params={"action": "render"}
        except Exception as e:
            logger.info(f'error: requests: {title}; {e}')
            return None
        if '|' in title:
            logger.debug("'|' in title: {title}")
        if r.status_code != 200:
            logger.error(f'HTTPerror {r.status_code} ({r.reason}): {title}')
        if len(r.text) < 200:
            logger.error(f'error: len(r.text) < 200 in page: {title}')
        text = r.text
        return text
