#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
from scripts.scan_pages import Scanner
from multiprocessing.dummy import Pool as ThreadPool
import concurrent.futures
import queue
import threading


# from multiprocessing import Pool
# from multiprocessing.pool import ThreadPool


class __ScannerMultithreads(Scanner):

    def ____do_scan(self):
        pool = ThreadPool(processes=None)  # processes equals CPU threads, usually 6—12
        limit = pool._processes - 1

        def process(page):
            pid, title = page
            err_refs = self.scan_page(title)
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
            err_refs = self.scan_page(title)
            if err_refs is None:
                pass
            self.db_update_pagedata(pid, err_refs)

    def _____do_scan(self, s):
        list_pages_for_scan = db_get_list_changed_pages()
        self.LOCK = threading.RLock()
        _queue = queue.Queue()
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


class ScannerMultithreads(Scanner):
    results = []

    def _scan_page(self, page):
        pid, title = page
        err_refs = self.scan_page(title)
        if err_refs is None:
            pass
        logging.info(f'db_update_pagedata: {title}')
        self.db_update_pagedata(pid, err_refs)

    def worker(self, _queue):
        while True:
            page = _queue.get()
            if page is None:
                break
            self._scan_page(page)
            _queue.task_done()

    def do_scan(self):
        queue_len = 1000
        threads_num = 15
        self.lock = threading.RLock()
        _queue = queue.Queue(maxsize=queue_len)
        threads = [threading.Thread(target=self.worker, args=(_queue,)) for i in range(threads_num)]
        [t.start() for t in threads]

        while True:
            pages = self.db_get_list_changed_pages(limit=3000)
            if not pages:
                break
            while pages:
                if _queue.empty():
                    for p in pages[:queue_len - 5]:
                        _queue.put(p)
            # block until all tasks are done
            _queue.join()

        # stop workers
        # for i in range(pages):
        #     _queue.put(None)
        [t.join() for t in threads]


class ____ScannerMultithreads(Scanner):
    queue_to_scanpages: queue.Queue
    queue_to_upd_pagesdata: queue.Queue
    event: threading.Event

    def ___db_get_list_changed_pages(self):
        limit = 3
        pages = self.db_get_list_changed_pages(limit)
        while not self.event.is_set() or self.queue_to_scanpages.empty():
            self.queue_to_scanpages.put(pages)
        if pages:
            self._db_get_list_changed_pages()

    def _db_get_list_changed_pages(self):
        # limit = 3
        # pages = self.db_get_list_changed_pages(limit)
        # while not self.event.is_set() or self.queue_to_scanpages.empty():
        #     self.queue_to_scanpages.put(pages)
        # if pages:
        #     self._db_get_list_changed_pages()
        # if not pages:
        #     break
        while not self.event.is_set() and self.queue_to_scanpages.empty():
            pages = self.db_get_list_changed_pages(limit=3)
            if not pages:
                break
            self.queue_to_scanpages.put(pages)

    def ____db_get_list_changed_pages(self, pages):
        while not self.event.is_set() and pages:
            self.queue_to_scanpages.put(pages)

    def _scan_page(self):
        while not self.event.is_set():  # or not self.queue_to_scanpages.empty():
            pages = self.queue_to_scanpages.get()
            for page in pages:
                pid, title = page
                err_refs = self.scan_page(title)
                if not err_refs:
                    continue
                self.queue_to_upd_pagesdata.put((pid, err_refs))

    def _db_update_pagedata(self):
        while not self.event.is_set() or not self.queue_to_upd_pagesdata.empty():
            pid, err_refs = self.queue_to_upd_pagesdata.get()
            self.db_update_pagedata(pid, err_refs)

    def do_scan(self):
        # limit = 3
        pages = self.db_get_list_changed_pages()
        if not pages:
            return
        self.queue_to_scanpages = queue.Queue(maxsize=100)
        self.queue_to_upd_pagesdata = queue.Queue(maxsize=100)
        self.event = threading.Event()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # while self.queue_to_scanpages.:
            # self.queue_to_scanpages.put(pages)
            # executor.submit(self._db_get_list_changed_pages, pages)
            # executor.submit(self._scan_page)
            # executor.submit(self._db_update_pagedata)
            # self.event.set()
            # self.queue_to_scanpages.put((p for p in pages))
            # map(self.queue_to_scanpages.put, pages)
            # for p in pages: self.queue_to_scanpages.put(p)
            # executor.submit(self._db_get_list_changed_pages, pages)
            executor.submit(self._scan_page)
            executor.submit(self._db_update_pagedata)
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
    #     # pipeline1 = queue.Queue(maxsize=1000)
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
#     q = queue.Queue()
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
