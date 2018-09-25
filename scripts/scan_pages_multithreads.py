#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
# import threading
from scripts.scan_pages import open_requests_session, db_get_list_changed_pages, db_update_pagedata, ScanRefsOfPage
from multiprocessing.dummy import Pool as ThreadPool
from urllib.parse import quote


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


class Scanner():

    def scan_page_mp(self, p):
        """Сканирование страниц на ошибки"""
        pid, title = p
        # global s
        # if pid != 3690723:  continue  # For tests
        print(title)
        try:
            r = self.s.get(f'https://ru.wikipedia.org/wiki/{quote(title)}')
        except Exception as e:
            print(e)
        err_refs = ScanRefsOfPage(r.text)
        return pid, err_refs

    def do_multiprocessing(self, pool_size=None):
        limit, offset = 100, 0
        pages = db_get_list_changed_pages(limit, offset)
        self.s = open_requests_session()
        pool = ThreadPool(pool_size)

        while pages:
            results = pool.map(self.scan_page_mp, pages)
            for pid, err_refs in results:
                db_update_pagedata(pid, err_refs)
            offset = offset + limit
            pages = db_get_list_changed_pages(limit, offset)

        pool.close()
        pool.join()
        self.s.close()

# workerthreadlist = []
# for x in range(0, 3):
# 	newthread = WorkerThread(url_list, url_list_lock)
# 	workerthreadlist.append(newthread)
# 	newthread.start()
# for x in range(0, 3):
# 	workerthreadlist[x].join()
