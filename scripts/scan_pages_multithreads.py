#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
# import threading
from scripts.scan_pages import Scanner
from multiprocessing.dummy import Pool as ThreadPool




class ScannerMultithreads(Scanner):

    def do_scan(self):
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
