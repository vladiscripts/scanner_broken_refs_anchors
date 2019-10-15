#!/usr/bin/env python3
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
from scripts.__init__ import *
from datetime import datetime
from settings import *
from scripts import scan_pages
from scripts import scan_pages_multithreads
from scripts.db_update import UpdateDB
from scripts.make_listspages import save_listpages_for_add_warning_tpls, save_listpages_for_remove_warning_tpls
from scripts.make_wikilists import make_and_save_wikilist
from scripts.db_models import Session

if __name__ == '__main__':
    t = datetime.now()
    logging.info(f'{t} Start scanner')

    db = Session()
    db_update = UpdateDB(db)

    # Опциональные чистки, проще (?) удалить и пересоздать файл базы данных
    # удаление метки проверки у страниц имеющих warning-шаблон

    if clear_timechecks_of_erropages:
        logging.info('*** Clear_timechecks_of_erropages')
        db_update.drop_timechecks_of_erropages()
    if clear_check_pages_with_warnings:
        logging.info('*** Clear_check_pages_with_warnings')
        db_update.drop_check_pages_with_warnings()
    # сброс всех меток проверки
    if clear_all_check_pages:
        logging.info('*** Clear_all_check_pages')
        db_update.drop_all_check_pages()
        db_update.drop_all_refs()

    # Сканирование и обновление базы данных
    if generate_lists:
        if update_db_from_wiki:
            logging.info('*** Update_db_from_wiki')
            # Обновление списка страниц имеющих warning-шаблон, шаблоны сносок,
            # и очистка базы от устарелых данных
            db_update.listpages()

        # старт сканирования
        logging.info('*** Doing start scan pages')
        # Run asyncio have problem on this server
        # if scan_asyncio:
        #   from scripts.scan_pages_asyncio import Scanner
        # 	scaner = Scanner()
        # 	scaner.do_scan()

        if multithreads:
            scanner = scan_pages_multithreads.ScannerMultithreads()
        else:
            scanner = scan_pages.Scanner()
        scanner.do_scan()

        # Запись списков
        logging.info('*** Doing save_listpages_for_remove_warning_tpls')
        save_listpages_for_remove_warning_tpls(db)
        logging.info('*** Doing save_listpages_for_add_warning_tpls')
        save_listpages_for_add_warning_tpls(db)
        logging.info('*** Doing make_wikilist')
        make_and_save_wikilist(db)
    Session.remove()
