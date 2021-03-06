#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import asyncio
import aiohttp
import socket
from urllib.parse import quote
from scripts.scan_pages import db_get_list_changed_pages, scan_page
from scripts.scan_refs_of_page import ScanRefsOfPage
from settings import *


class Scanner:
    def do_scan(self):
        """Сканирование страниц на ошибки"""
        list_pages_for_scan = db_get_list_changed_pages()

        loop = asyncio.get_event_loop()
        loop.run_until_complete(self.asynchronous(list_pages_for_scan, loop))
        loop.close()

    async def asynchronous(self, list_pages, loop):
        headers = {'user-agent': 'user:textworkerBot'}
        sem = asyncio.Semaphore(limit_asynch_threads)
        conn = aiohttp.TCPConnector(family=socket.AF_INET, verify_ssl=False)
        async with aiohttp.ClientSession(headers=headers, connector=conn, loop=loop) as session:
            tasks = [asyncio.ensure_future(self.scan_pagehtml_for_referrors(sem, p, session)) for p in list_pages]
            finished, unfinished = await asyncio.wait(tasks)
            if len(unfinished):
                logging.error('have unfinished async tasks')

    async def db_works(self, p):
        scan_page(p)

    async def scan_pagehtml_for_referrors(self, sem, p, session):
        """Сканирование страницы на ошибки"""
        page_id, page_title = p[0], p[1]
        url = 'https://ru.wikipedia.org/wiki/' + quote(page_title)

        if page_title == 'None' or page_title is None:
            logging.error('!!!!!!!!!!!!!')

        async with sem:
            retries = 0
            while retries <= 5:
                try:
                    response = await session.request('GET', url, params={"action": "render"}, )  # timeout=30

                    if response.status == 200:
                        response_text = await response.text()
                        logging.info(page_title + ':')
                        page = ScanRefsOfPage(response_text)
                        errrefs = page.err_refs
                        # try:
                        # 	errrefs
                        # except:
                        # 	pass
                        await self.db_works([page_id, page_title, errrefs])
                        del page
                    elif response.status == 429:
                        # Too many requests
                        retries += 1
                        await asyncio.sleep(1)
                    else:
                        logging.error(page_title + ' response.status != 200')
                    response.close()
                    break

                except (aiohttp.ClientOSError, aiohttp.ClientResponseError,
                        aiohttp.ServerDisconnectedError, asyncio.TimeoutError) as e:
                    logging.error(
                        '!!! Error. Page title: "%s"; url: %s; error: %r. Can will work on a next request.' % (
                        page_title, url, e))
                    retries += 1
                    await asyncio.sleep(1)

# for test
# page = ScanRefsOfPage('2091672', 'Марк Фульвий Флакк (консул 125 года до н. э.)')
# pass
