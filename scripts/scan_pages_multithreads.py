#!/usr/bin/env python
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
import time
from config import *
from scripts.db import session, Page, Ref, WarningTpls, Timecheck, queryDB
from scripts.scan_refs_of_page import ScanRefsOfPage
import urllib.request
from threading import Thread
import threading
from threading import BoundedSemaphore


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
def worker_Semaphore(sema, p):
	scan_page(sema, p)
	# releasing the thread increments the sema value
	sema.release()


def do_work_threading_Semaphore():
	list_pages_for_scan = db_get_list_pages_for_scan()
	# url_list_lock = threading.Lock()

	limit = 5
	pool_sema = threading.BoundedSemaphore(limit)
	threads = []
	for p in list_pages_for_scan:
		# pool_sema.acquire()
		# # page_id, page_title = p[0], p[1]
		# p = tuple(p)
		# t = threading.Thread(target=worker, args={p, pool_sema})
		# t.start()
		# threads.append(t)

		with pool_sema:
			# page_id, page_title = p[0], p[1]
			p = tuple(p)
			t = threading.Thread(target=worker, args={p, pool_sema})
			t.start()
			threads.append(t)
			scan_page(pool_sema, p)

		# try:
		# 	pool_sema.acquire()
		# 	t = threading.Thread(target=scan_page, args={p, pool_sema})
		# 	t.start()
		# 	threads.append(t)
		# # exit once the user hit CTRL+c
		# # or you can make the thead as daemon t.setdaemon(True)
		# except KeyboardInterrupt:
		# 	exit()
		pass
	pass


import queue




def worker(q):
	while True:
		item = q.get()
		if item is None:
			break
		scan_page(item)
		q.task_done()


def do_work_threading():
	list_pages_for_scan = db_get_list_pages_for_scan()
	q = queue.Queue()
	threads = []
	for i in range(3):
		t = threading.Thread(target=worker, args=(q,))
		t.start()
		threads.append(t)

	for item in list_pages_for_scan:
		q.put(item)

	# block until all tasks are done
	q.join()

	# stop workers
	for i in range(list_pages_for_scan):
		q.put(None)
	for t in threads:
		t.join()



# workerthreadlist = []
# for x in range(0, 3):
# 	newthread = WorkerThread(url_list, url_list_lock)
# 	workerthreadlist.append(newthread)
# 	newthread.start()
# for x in range(0, 3):
# 	workerthreadlist[x].join()


def do_scan():
	"""Сканирование страниц на ошибки"""
	# pages_for_scan = db_get_list_pages_for_scan()
	# for p in pages_for_scan:
	for p in db_get_list_pages_for_scan():
		page_id, page_title = p[0], p[1]

		# For tests
		# if page_id != 273920:	continue

		# очистка db от списка старых ошибок
		session.query(Ref).filter(Ref.page_id == page_id).delete()
		session.query(Timecheck).filter(Timecheck.page_id == page_id).delete()
		# session.flush()
		# сканирование страниц на ошибки
		r = s.get('https://ru.wikipedia.org/wiki/' + quote(title))
		page = ScanRefsOfPage(r.text)
		ref_no_doubles = []
		for ref in page.err_refs:
			session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
		# try:
		# 	session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
		# except IntegrityError:
		# 	pass
		# except:
		# 	pass

		# session.query(Ref).filter_by(page_id = page_id, citeref = ref['citeref']).delete()
		# if session.query(Ref).filter_by(page_id = page_id, citeref = ref['citeref']) .count() < 1:
		# 	session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
		# 	session.commit()
		# if ref['citeref'] not in ref_no_doubles:
		# 	ref_no_doubles.append(ref['citeref'])
		# 	session.merge(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
		# 	session.flush()

		# try:
		# 	session.merge(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
		# except:
		# 	pass
		# for ref in page.err_refs:
		# 	# try:
		# 	# 	x = session.query(Ref).filter_by(Ref.page_id = page_id, Ref.citeref = ref['citeref']).first()
		# 	# except:
		# 	# 	pass
		# 	x = session.query(Ref).filter_by(page_id=page_id, citeref=ref['citeref']).first()
		# 	if not x:
		# 		# 	session.query(Ref).filter(page_id=page_id, citeref=ref['citeref']).update(r)
		# 		# else:
		# 		try:
		# 			session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
		# 		except:
		# 			pass
		time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
		# session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: time_current})
		session.add(Timecheck(page_id, time_current))
		# try:
		# 	session.flush()
		# except:
		# 	pass
		# session.flush()
		session.commit()


def db_get_list_pages_for_scan():
	return queryDB(session.query(Page.page_id, Page.title) \
				   .select_from(Page) \
				   .outerjoin(Timecheck, Page.page_id == Timecheck.page_id) \
				   .filter((Timecheck.timecheck.is_(None)) | (Page.timeedit > Timecheck.timecheck)))


def scan_page(p):
	"""Сканирование страниц на ошибки"""
	page_id, page_title = p[0], p[1]

	# очистка db от списка старых ошибок
	session.query(Ref).filter(Ref.page_id == page_id).delete()
	session.query(Timecheck).filter(Timecheck.page_id == page_id).delete()

	# сканирование страниц на ошибки
	r = s.get('https://ru.wikipedia.org/wiki/' + quote(title))
	page = ScanRefsOfPage(r.text)
	for ref in page.err_refs:
		session.add(Ref(page_id, ref['citeref'], ref['link_to_sfn'], ref['text']))
	time_current = time.strftime('%Y%m%d%H%M%S', time.gmtime())
	# session.query(Page).filter(Page.page_id == page_id).update({Page.timecheck: time_current})
	session.add(Timecheck(page_id, time_current))
	session.commit()
