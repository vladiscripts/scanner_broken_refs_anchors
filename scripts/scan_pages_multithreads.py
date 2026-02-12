#!/usr/bin/env python
# author: https://github.com/vladiscripts
#
from queue import Queue
from threading import Thread, RLock
from scripts.scan_pages import Scanner, db_update_pagedata_, db_get_list_changed_pages, PageData
from scripts.db_models import Session
from scripts import datetime, logger


class ScannerMultithreads(Scanner):
    test = False

    def __init__(self):
        super().__init__()
        self.threads_num = 16
        self.pages_limit_by_query = 300
        queue_len = 1000
        # self.threads_num = 3
        # self.pages_limit_by_query = 3
        # queue_len = 3
        self.queue_toscan = Queue(maxsize=queue_len)
        self.db_lock = RLock()

    def crawler(self):
        logger.debug(f'worker start, unfinished_tasks={self.queue_toscan.unfinished_tasks}')
        while True:
            page = self.queue_toscan.get()
            if page is None:
                self.queue_toscan.task_done()
                break
            pid, title = page
            if self.test:
                logger.info(f'scan: {title}')
            else:
                logger.info(f'scan: {title}')
                err_refs = self.scan_page(title, pid)
                if err_refs is None:
                    # db_delete_page_id(pid)  # Не чистим ДБ от этой страницы здесь — это делается в другом скрипте
                    continue
                with Session() as s:  # Создаём новую сессию для обновления данных
                    db_update_pagedata_(s, PageData(title, pid, err_refs), datetime.utcnow())
            self.queue_toscan.task_done()
        logger.debug(f'worker end, unfinished_tasks={self.queue_toscan.unfinished_tasks}')

    def pages_feed(self):
        logger.debug(f'thread_pages')
        k = []
        c = 0
        while True:
            c += 1
            with Session() as s:
                pages = db_get_list_changed_pages(limit=self.pages_limit_by_query)
            if not pages:
                for i in range(self.threads_num):
                    self.queue_toscan.put(None)
                break
            for p in pages:
                # p = pages.pop()
                self.queue_toscan.put(p)
                if p in k:
                    logger.info(f'p in k: {p}')
                k.append(p)
            self.queue_toscan.join()
        # Session.remove()
        # s.close()
        logger.debug(f'self.queue_toscan {self.queue_toscan.unfinished_tasks}')
        logger.debug(f'thread_pages end')

    def do_scan(self, test=False):
        self.test = test
        t_pages = Thread(target=self.pages_feed, name='pages_feed')
        t_pages.start()

        logger.debug(f't.start()')
        t_crawlers = [Thread(target=self.crawler, name=f'crawler-{i}') for i in range(self.threads_num)]
        [t.start() for t in t_crawlers]

        [t.join() for t in t_crawlers]
        logger.debug(f'end threads')


if __name__ == '__main__':
    scanner = ScannerMultithreads()
    scanner.do_scan()
