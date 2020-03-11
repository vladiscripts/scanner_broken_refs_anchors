#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
from multiprocessing.dummy import Pool as ThreadPool
import concurrent.futures
from queue import Queue
import threading
from threading import Thread, RLock, Event
from scripts.logger import logger
# from scripts import *
from scripts.scan_pages import Scanner, db_update_pagedata_, db_update_pagedata__, db_get_list_changed_pages


# from multiprocessing import Pool
# from multiprocessing.pool import ThreadPool


class __ScannerMultithreads(Scanner):

    def ____do_scan(self):
        pool = ThreadPool(processes=None)  # processes equals CPU threads, usually 6—12
        limit = pool._processes - 1

        def process(page):
            pid, title = page
            err_refs = self.scan_page(None, title)
            if err_refs is None:
                pass
            self.db_update_pagedata(pid, err_refs)

        # for results in pool.map(process, self.db_get_list_changed_pages(limit), 1):  pass
        pool.map(process, self.db_get_list_changed_pages(limit), 1)

        pool.close()
        pool.join()
        self.s.close()

    #


class ___ScannerMultithreads(Scanner):
    def worker(self, _queue, page):
        with self.LOCK.acquire() as lock:

            page = _queue.get()

            while True:
                item = _queue.get()
                if item is None:
                    break
                scan_results = scan_page(s, item[1])
                db_update_pagedata(item[0], scan_results.err_refs)
                q.task_done()

            pid, title = page
            err_refs = self.scan_page(None, title)
            if err_refs is None:
                pass
            self.db_update_pagedata(pid, err_refs)

    def _____do_scan(self, s):
        list_pages_for_scan = db_get_list_changed_pages()
        self.LOCK = threading.RLock()
        _queue = Queue()
        threads = []
        for i in range(12):
            thread = threading.Thread(target=self.worker, args=(_queue, s,))
            thread.start()
            threads.append(thread)

        for item in list_pages_for_scan:
            _queue.put(item)

        # block until all tasks are done
        _queue.join()

        # stop workers
        for i in range(list_pages_for_scan):
            _queue.put(None)
        for t in threads:
            t.join()


class ____ScannerMultithreads(Scanner):
    results = []

    # def _scan_page(self, page):
    #     pid, title = page
    #     err_refs = self.scan_page(title)
    #     if err_refs is None:
    #         pass
    #     logger.info(f'db_update_pagedata: {title}')
    #     with self.lock:
    #         self.db_update_pagedata(pid, err_refs)

    def _load_pages(self):
        # while True:
        pages = []
        if not pages:
            # break
            pages = self.db_get_list_changed_pages(limit=3000)
            if not pages:
                self._queue_toscan.task_done()
                self.done = True
                return
            while pages:
                if self._queue_toscan.empty():
                    for p in pages[:queue_len - 5]:
                        self._queue_toscan.put(p)

    # def _scan_page(self, page):
    def _scan_page(self):
        # while True:
        if not self._queue_toscan.empty():
            page = self._queue_toscan.get()
            if page is None:
                # break
                return
            pid, title = page
            err_refs = self.scan_page(None, title)
            self._queue_toscan.put((title, pid, err_refs))
            # self._queue_toscan.task_done()

    def _to_db(self):
        # with self.lock:
        if not self._queue_toscan.empty():
            title, pid, err_refs = self._queue_toscan.get()
            logger.info(f'db_update_pagedata: {title}')
            self.db_update_pagedata(pid, err_refs)

    def worker(self, _queue_toscan):
        while True:
            page = _queue_toscan.get()
            if page is None:
                break
            self._scan_page(page)
            self._to_db()
        # self._scan_page()
        # self._to_db()

    def do_scan(self):
        queue_len = 1000
        threads_num = 16
        self.lock = threading.RLock()
        self._queue_toscan = Queue(maxsize=queue_len)
        self._queue_todb = Queue(maxsize=queue_len)
        threads = [threading.Thread(target=self.worker, args=(self._queue_toscan,)) for i in range(threads_num)]
        [t.start() for t in threads]

        while True:
            pages = self.db_get_list_changed_pages(limit=3000)
            if not pages:
                break
            while pages:
                if self._queue_toscan.empty():
                    for p in pages[:queue_len - 5]:
                        self._queue_toscan.put(p)
        # block until all tasks are done
        self._queue_toscan.join()

        # stop workers
        # for i in range(pages):
        #     _queue.put(None)
        [t.join() for t in threads]


uniqs = set()


class ScannerMultithreads(Scanner):

    # def _scan_page(self, page):
    def call_scan_page(self):
        # while True:
        logger.debug(f'_scan_page {not self.queue_toscan.empty()}')
        # while True:
        for page in self.list_pages_for_scan:
            # self.queue_toscan.put(p)

            # evt = threading.Event()
            # page = self.queue_toscan.get()
            # if not page:
            #     return
            pid, title = page
            logger.info(f'scan: {title}')
            err_refs = self.scan_page(None, title)
            self.queue_todb.put((title, pid, err_refs,
                                 # evt
                                 ))
            # self.queue_toscan.task_done()
            # evt.wait()

    def to_db(self):
        logger.debug(f'_to_db  not self.queue_todb.empty()  {not self.queue_todb.empty()}')
        # if not self.queue_todb.empty():
        while True:
            # logger.debug(f'_to_db1')
            title, pid, err_refs = self.queue_todb.get()
            logger.info(f'db_update_pagedata: {title}')
            self.db_update_pagedata(title, pid, err_refs)

            # # Глючно, требуется синхронизация, fetch SQLAlchemy
            # if self.queue_todb.qsize() >= 2 or self.workers_done:
            #     pages = [self.queue_todb.get() for i in range(100)]
            #     with self.lock:
            #         self.db_update_pagedata_packet(pages)
            # if self.workers_done:
            #     break

            # self.queue_toscan.task_done()

    def _worker(self, _queue_toscan):
        # while True:
        #     page = _queue_toscan.get()
        #     if page is None:
        #         break
        #     self._scan_page(page)
        #     self._to_db()
        logger.debug(f'worker start, '
                     # f'queue_toscan={self.queue_toscan.queue}, '
                     f'unfinished_tasks={self.queue_toscan.unfinished_tasks}')
        # p = self.list_pages_for_scan.pop()
        # self.queue_toscan.put(p)
        self.call_scan_page()
        logger.debug(f'in lock')
        with self.lock:
            self.to_db()
        logger.debug(f'unlock')
        # evt.set()
        self.queue_toscan.task_done()
        logger.debug(f'worker end, '
                     # f'queue_toscan={self.queue_toscan.queue}, '
                     f'unfinished_tasks={self.queue_toscan.unfinished_tasks}')

    def crawler(self):
        # while True:
        #     page = _queue_toscan.get()
        #     if page is None:
        #         break
        #     self._scan_page(page)
        #     self._to_db()
        logger.debug(f'worker start, '
                     # f'queue_toscan={self.queue_toscan.queue}, '
                     f'unfinished_tasks={self.queue_toscan.unfinished_tasks}')
        # p = self.list_pages_for_scan.pop()
        # self.queue_toscan.put(p)

        #
        # self.call_scan_page()
        # logger.debug(f'_scan_page {not self.queue_toscan.empty()}')

        # logger.debug(f'db_updating: {title}')
        from scripts.db_models import PageWithSfn, ErrRef, Timecheck, Session
        s = Session()
        # Session.rollback()

        while True:

            # for page in self.list_pages_for_scan:

            # self.queue_toscan.put(p)

            # evt = threading.Event()
            # with self.lock:
            page = self.queue_toscan.get()
            if page is None:
                break
            pid, title = page

            # logger.info(f'scan: {title}')
            err_refs = self.scan_page(None, title)
            # self.queue_todb.put((title, pid, err_refs,
            #                      # evt
            #                      ))

            logger.debug(f'in lock {title}')
            # with self.lock:
            #
            # self.to_db()

            # logger.debug(f'_to_db  not self.queue_todb.empty()  {not self.queue_todb.empty()}')
            # if not self.queue_todb.empty():
            # while True:

            # logger.debug(f'_to_db1')
            # title, pid, err_refs, evt = self.queue_todb.get()
            # title, pid, err_refs = self.queue_todb.get()

            # logger.info(f'db_update_pagedata: {title}')
            # self.db_update_pagedata(title, pid, err_refs)
            db_update_pagedata_(s, title, pid, err_refs)

            # evt.set()
            self.queue_toscan.task_done()

            logger.debug(f'unlock {title}')

            # evt.set()
            # self.queue_toscan.task_done()

        Session.remove()
        # logger.debug(f'db_updated: {title}')

        logger.debug(f'worker end, '
                     # f'queue_toscan={self.queue_toscan.queue}, '
                     f'unfinished_tasks={self.queue_toscan.unfinished_tasks}')

        # while True:
        #     pages = self.db_get_list_changed_pages(limit=3000)
        #     if not pages:
        #         break
        #     while pages:
        #         if self._queue_toscan.empty():
        #             for p in pages[:queue_len - 5]:
        #                 self._queue_toscan.put(p)

    def thread_pages(self, pages_limit_by_query=3000):
        logger.debug(f'thread_pages')

        while True:
            pages = db_get_list_changed_pages(limit=pages_limit_by_query)
            if not pages:
                for i in range(self.threads_num):
                    self.queue_toscan.put(None)
                break
            while pages:
                if not self.queue_toscan.full():
                    p = pages.pop()

                    # title = p[1]
                    # if title in uniqs:
                    #     logger.info(f'!!!uniqs: {title}')
                    # uniqs.add(title)

                    self.queue_toscan.put(p)

        logger.debug(f'self.queue_toscan {self.queue_toscan.unfinished_tasks}')
        logger.debug(f'thread_pages end')

    def do_scan(self):
        # self.workers_done = False
        queue_len = 1000
        self.threads_num = 16
        self.lock = RLock()
        # self.queue_pages = Queue(maxsize=queue_len)
        self.queue_toscan = Queue(maxsize=queue_len)
        # self.queue_todb = Queue(maxsize=0)

        # self.list_pages_for_scan = self.db_get_list_changed_pages(limit=2)
        # for p in self.list_pages_for_scan:
        #     self.queue_toscan.put(p)

        t_pages = Thread(target=self.thread_pages)
        t_pages.start()

        # if not self.queue_toscan.empty():
        t_crawlers = [Thread(target=self.crawler,
                             # daemon=True
                             ) for i in range(self.threads_num)]
        logger.debug(f't.start()')
        [t.start() for t in t_crawlers]

        # t_db = Thread(target=self.to_db, daemon=True)
        # t_db.start()

        # block until all tasks are done
        # self.queue_pages.join()
        self.queue_toscan.join()
        # self.queue_todb.join()

        # stop workers
        # for i in range(pages):
        #     _queue.put(None)

        # t_pages.join()
        [t.join() for t in t_crawlers]
        # t_db.join()
        # self.workers_done = True
        logger.debug(f'end threads')


class _ScannerMultithreads(Scanner):
    queue_to_scanpages: Queue
    queue_to_upd_pagesdata: Queue
    event: Event

    def ___db_get_list_changed_pages(self):
        limit = 3
        pages = self.db_get_list_changed_pages(limit)
        while not self.event.is_set() or self.queue_to_scanpages.empty():
            self.queue_to_scanpages.put(pages)
        if pages:
            self._db_get_list_changed_pages()

    def _db_get_list_changed_pages(self, pages):
        # limit = 3
        # pages = self.db_get_list_changed_pages(limit)
        # while not self.event.is_set() or self.queue_to_scanpages.empty():
        #     self.queue_to_scanpages.put(pages)
        # if pages:
        #     self._db_get_list_changed_pages()
        # if not pages:
        #     break
        while not self.event.is_set():
            # pages = self.db_get_list_changed_pages(limit=3)
            # if not pages:
            #     break
            # self.queue_to_scanpages.put(pages)

            # for p in pages:
            #     self.queue_to_scanpages.put(p)

            # while True:
            pages = []
            if not pages:
                pages = self.db_get_list_changed_pages(limit=3000)
                if not pages:
                    break
            while pages:
                if self.queue_to_scanpages.empty():
                    for p in pages[:self.queue_to_scanpages.maxsize]:
                        self.queue_to_scanpages.put(p)

        # while True:
        #     pages = self.db_get_list_changed_pages(limit=3000)
        #     if not pages:
        #         break
        #     while pages:
        #         if self.queue_to_scanpages.empty():
        #             for p in pages[:queue_to_scanpages_len - 5]:
        #                 self.queue_to_scanpages.put(p)

    def ____db_get_list_changed_pages(self, pages):
        while not self.event.is_set() and pages:
            self.queue_to_scanpages.put(pages)

    def _scan_page(self):
        while not self.event.is_set() and not self.queue_to_upd_pagesdata.empty():  # or not self.queue_to_scanpages.empty():
            page = self.queue_to_scanpages.get()
            pid, title = page
            err_refs = self.scan_page(None, title)
            if not err_refs:
                continue
            self.queue_to_upd_pagesdata.put((title, pid, err_refs))

    def _db_update_pagedata(self):
        while not self.event.is_set() or not self.queue_to_upd_pagesdata.empty():
            title, pid, err_refs = self.queue_to_upd_pagesdata.get()
            logger.info(f'db_update_pagedata: {title}')
            self.db_update_pagedata(pid, err_refs)

    def do_scan(self):
        queue_to_scanpages_len = 100
        threads_num = 16
        self.queue_to_scanpages = Queue(maxsize=queue_to_scanpages_len)
        self.queue_to_upd_pagesdata = Queue(maxsize=100)
        self.event = Event()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # while self.queue_to_scanpages.:
            # self.queue_to_scanpages.put(pages)
            # executor.submit(self._db_get_list_changed_pages)
            # executor.submit(self._scan_page)
            # executor.submit(self._db_update_pagedata)
            # self.event.set()
            # self.queue_to_scanpages.put((p for p in pages))
            # map(self.queue_to_scanpages.put, pages)
            # for p in pages: self.queue_to_scanpages.put(p)
            # executor.submit(self._db_get_list_changed_pages, pages)

            executor.submit(self._scan_page)
            executor.submit(self._db_update_pagedata)

            pages = []
            while True:
                if not pages:
                    pages = self.db_get_list_changed_pages(limit=3000)
                    if not pages:
                        break
                if self.queue_to_scanpages.empty():
                    for p in pages[:queue_to_scanpages_len]:
                        self.queue_to_scanpages.put(p)

            # executor.submit(self._db_get_list_changed_pages)

            self.event.set()

    #

    # def _scan_page(self, event):
    #     limit = 1000
    #     while not event.is_set():
    #         pages = self.db_get_list_changed_pages(limit)
    #         for page in pages:
    #             pid, title = page
    #             err_refs = self.scan_page(title)
    #             if err_refs is None:
    #                 pass
    #             self.db_update_pagedata(pid, err_refs)
    #
    # def do_scan(self):
    #     # pipeline1 = Queue(maxsize=1000)
    #     event = threading.Event()
    #     with concurrent.futures.ThreadPoolExecutor() as executor:
    #         executor.submit(self._scan_page, event)
    #         event.set()

    # def _do_scan(self, pool_size=None):
    #     limit = 10
    #     # offset, limit = 0, 100
    #     # self.s = open_requests_session()
    #     pool = ThreadPool(pool_size)
    #
    #     while True:
    #         # pages = self.db_get_list_changed_pages(offset, limit)
    #         pages = self.db_get_list_changed_pages(limit)
    #         if not pages:
    #             break
    #         results = pool.map(self.scan_page, pages)
    #         for pid, err_refs in results:
    #             # Вероятно здесь ошибка.
    #             # - Не обрабатываются некоторые страницы, т.ч. не удаляются их ErrRefs.
    #             # Поэтому в уже исправленные статьи повторно ставится предупреждение.
    #             # Удалять предваритьльно до проверки страницы ErrRefs нельзя, это вызовет тоже сбойные простановки.
    #             # Не сканировать тоже нельзя, ио люди жалуются на повторные простановки.
    #             # Значит надо сканировать, и может перепроверять флаги начала и конца проверки каждой страницы,
    #             # перепроверяя при ошибке. Но вероятны опять глюки мультипотоков.
    #             #
    #             # Не, при однопоточном скане таже проблема.
    #             # (Проверяю по ДБ 1pagesrefs.sqlite с. "Английская_революция" (54229). Там шаблон должен сниматься,
    #             # время проверки позже времени редактирования.)
    #             # Почему-то страница в отладчике проверяется, если пропускать все страницы кроме этой.
    #             # Но в запуске без пропусков, по всем страницам, делает ошибку.
    #
    #             # if pid != 54229: continue
    #             if err_refs is not None:
    #                 self.db_update_pagedata(pid, err_refs)
    #             # else: print()
    #         # offset = offset + limit
    #
    #     pool.close()
    #     pool.join()
    #     self.s.close()
    #
    # def ___do_scan(self, pool_size=None):
    #     limit = 10
    #     # offset, limit = 0, 100
    #     # self.s = open_requests_session()
    #     pool = ThreadPool(pool_size)
    #
    #     while True:
    #         # pages = self.db_get_list_changed_pages(offset, limit)
    #         pages = self.db_get_list_changed_pages(limit)
    #         if not pages:
    #             break
    #         results = pool.imap(self.scan_page, pages)
    #         for pid, err_refs in results:
    #             # Вероятно здесь ошибка.
    #             # - Не обрабатываются некоторые страницы, т.ч. не удаляются их ErrRefs.
    #             # Поэтому в уже исправленные статьи повторно ставится предупреждение.
    #             # Удалять предваритьльно до проверки страницы ErrRefs нельзя, это вызовет тоже сбойные простановки.
    #             # Не сканировать тоже нельзя, ио люди жалуются на повторные простановки.
    #             # Значит надо сканировать, и может перепроверять флаги начала и конца проверки каждой страницы,
    #             # перепроверяя при ошибке. Но вероятны опять глюки мультипотоков.
    #             #
    #             # Не, при однопоточном скане таже проблема.
    #             # (Проверяю по ДБ 1pagesrefs.sqlite с. "Английская_революция" (54229). Там шаблон должен сниматься,
    #             # время проверки позже времени редактирования.)
    #             # Почему-то страница в отладчике проверяется, если пропускать все страницы кроме этой.
    #             # Но в запуске без пропусков, по всем страницам, делает ошибку.
    #
    #             # if pid != 54229: continue
    #             if err_refs is not None:
    #                 self.db_update_pagedata(pid, err_refs)
    #             # else: print()
    #         # offset = offset + limit
    #
    #     pool.close()
    #     pool.join()
    #     self.s.close()

# workerthreadlist = []
# for x in range(0, 3):
# 	newthread = WorkerThread(url_list, url_list_lock)
# 	workerthreadlist.append(newthread)
# 	newthread.start()
# for x in range(0, 3):
# 	workerthreadlist[x].join()


# class WorkerThread(threading.Thread):
# 	def __init__(self, url_list, url_list_lock):
# 		super(WorkerThread, self).__init__()
# 		self.url_list = url_list
# 		self.url_list_lock = url_list_lock
# 		self.maxconnections = 5
#
# 	def run(self):
#
#
#
# 		self.pool_sema.acquire()
#
# 		nexturl = self.grab_next_url()
# 		if nexturl == None: break
# 		self.retrieve_url(nexturl)
# 		pass
#
# 		self.pool_sema.release()
#
#
# 	def grab_next_url(self):
#
#
# 		self.url_list_lock.acquire(1)
# 		if len(self.url_list) < 1:
# 			nexturl = None
# 		else:
# 			nexturl = self.url_list[0]
# 			del self.url_list[0]
# 		self.url_list_lock.release()
# 		return nexturl
#
# 	def retrieve_url(self, nexturl):
# 		p = nexturl
# 		# page_id = p[0]
# 		# page_title = p[1]
# 		# url = 'https://ru.wikipedia.org/wiki/' + quote(page_title)
# 		scan_page(p)


# defining our worker and pass a counter and the semaphore to it
# def worker_Semaphore(sema, p):
#     scan_page(sema, p)
#     # releasing the thread increments the sema value
#     sema.release()
#
#
# def do_work_threading_Semaphore():
#     s = open_requests_session()
#     list_pages_for_scan = db_get_list_changed_pages()
#     # url_list_lock = threading.Lock()
#
#     limit = 5
#     pool_sema = threading.BoundedSemaphore(limit)
#     threads = []
#     for p in list_pages_for_scan:
#         # pool_sema.acquire()
#         # # page_id, page_title = p[0], p[1]
#         # p = tuple(p)
#         # t = threading.Thread(target=worker, args={p, pool_sema})
#         # t.start()
#         # threads.append(t)
#
#         with pool_sema:
#             # page_id, page_title = p[0], p[1]
#             p = tuple(p)
#             t = threading.Thread(target=worker, args={p, pool_sema})
#             t.start()
#             threads.append(t)
#             scan_results = scan_page(pool_sema, p[1])
#             db_update_pagedata(p[0], scan_results.err_refs)
#
#         # try:
#         # 	pool_sema.acquire()
#         # 	t = threading.Thread(target=scan_page, args={p, pool_sema})
#         # 	t.start()
#         # 	threads.append(t)
#         # # exit once the user hit CTRL+c
#         # # or you can make the thead as daemon t.setdaemon(True)
#         # except KeyboardInterrupt:
#         # 	exit()
#         pass
#     pass
#
#
# import queue
#
#
# def worker(q, s):
#     while True:
#         item = q.get()
#         if item is None:
#             break
#         scan_results = scan_page(s, item[1])
#         db_update_pagedata(item[0], scan_results.err_refs)
#         q.task_done()
#
#
# def do_work_threading(s):
#     list_pages_for_scan = db_get_list_changed_pages()
#     q = Queue()
#     threads = []
#     for i in range(3):
#         t = threading.Thread(target=worker, args=(q, s,))
#         t.start()
#         threads.append(t)
#
#     for item in list_pages_for_scan:
#         q.put(item)
#
#     # block until all tasks are done
#     q.join()
#
#     # stop workers
#     for i in range(list_pages_for_scan):
#         q.put(None)
#     for t in threads:
#         t.join()
