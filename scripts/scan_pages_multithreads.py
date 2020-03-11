#!/usr/bin/env python
# author: https://github.com/vladiscripts
#
from queue import Queue
import threading
from threading import Thread, RLock
import time
from scripts.logger import logger
# from scripts import *
from scripts.scan_pages import Scanner, db_update_pagedata_, db_update_pagedata__, db_get_list_changed_pages, \
    time_current
from scripts.db_models import Session, db_session as s


class ScannerMultithreads(Scanner):
    test = False

    def __init__(self):
        super().__init__()
        # self.threads_num = 16
        # self.pages_limit_by_query = 300
        # queue_len = 1000
        self.threads_num = 3
        self.pages_limit_by_query = 3
        queue_len = 3
        self.queue_toscan = Queue(maxsize=queue_len)
        self.db_lock = RLock()

    def crawler(self):
        logger.debug(f'worker start, unfinished_tasks={self.queue_toscan.unfinished_tasks}')
        # s = Session()
        while True:
            page = self.queue_toscan.get()
            if page is None:
                self.queue_toscan.task_done()
                break
            pid, title = page
            if self.test:
                logger.info(f'scan: {title}')
            else:
                print(f'scan: {title}')
                # chktime = time_current()
                chktime = time.gmtime()
                err_refs = self.scan_page(title, pid)
                with self.db_lock:
                    db_update_pagedata_(s, title, pid, err_refs, chktime)
            self.queue_toscan.task_done()
            print()
        # Session.remove()
        # s.close()
        logger.debug(f'worker end, unfinished_tasks={self.queue_toscan.unfinished_tasks}')

    def pages_feed(self):
        logger.debug(f'thread_pages')
        k = []
        c = 0
        # s = Session()
        while True:
            c += 1
            pages = db_get_list_changed_pages(s, limit=self.pages_limit_by_query)
            # pages1 = pages.copy()
            # todo: дублируются сканирования страниц
            # todo: не записываются в БД ли не корректно читаются
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
                print()
            self.queue_toscan.join()
            print()
        # Session.remove()
        # s.close()
        logger.debug(f'self.queue_toscan {self.queue_toscan.unfinished_tasks}')
        logger.debug(f'thread_pages end')

    def do_scan(self, test=False):
        self.test = test
        t_pages = Thread(target=self.pages_feed, name='pages_feed')
        t_pages.start()

        logger.debug(f't.start()')
        t_crawlers = [Thread(target=self.crawler, name=f'crawler-{i}') for i in range(self.threads_num)]  # daemon=True
        [t.start() for t in t_crawlers]

        # self.queue_toscan.join()

        [t.join() for t in t_crawlers]
        logger.debug(f'end threads')


if __name__ == '__main__':
    scanner = ScannerMultithreads()
    scanner.do_scan()
