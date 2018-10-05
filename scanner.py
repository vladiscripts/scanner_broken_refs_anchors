#!/usr/bin/env python3
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
from datetime import datetime
from settings import *
# from scripts.scan_pages_asyncio import Scanner
# from scripts import scan_pages_multithreads
from scripts import scan_pages
from scripts.db_update import UpdateDB
from scripts.make_listspages import save_listpages_for_add_warning_tpls, save_listpages_for_remove_warning_tpls
from scripts.make_wikilists import make_and_save_wikilist

if __name__ == '__main__':
    t = datetime.now()
    print(f'{t} Start scanner')

    db_update = UpdateDB()

    # Опциональные чистки, проще (?) удалить и пересоздать файл базы данных
    # удаление метки проверки у страниц имеющих warning-шаблон
    if clear_check_pages_with_warnings:
        print('*** Doing clear_check_pages_with_warnings')
        db_update.drop_check_pages_with_warnings()
    # сброс всех меток проверки
    if clear_all_check_pages:
        print('*** Doing clear_all_check_pages')
        db_update.drop_all_check_pages()
        db_update.drop_all_refs()

    # Сканирование и обновление базы данных
    if do_generation_lists:
        if do_update_db_from_wiki:
            print('*** Doing update_db_from_wiki')
            # Обновление списка страниц имеющих warning-шаблон, шаблоны сносок,
            # и очистка базы от устарелых данных
            db_update.listpages()

        # старт сканирования
        print('*** Doing start scan pages')
        # Run asyncio have problem on this server
        # if scan_asyncio:
        # 	scaner = Scanner()
        # 	scaner.do_scan()
        # else:
        # 	scan_pages.do_scan()
        scan_pages.do_scan()

        # scaner = scan_pages_multithreads.Scanner()
        # scaner.do_multiprocessing()

        # Запись списков
        print('*** Doing save_listpages_for_remove_warning_tpls')
        save_listpages_for_remove_warning_tpls()
        print('*** Doing save_listpages_for_add_warning_tpls')
        save_listpages_for_add_warning_tpls()
        print('*** Doing make_wikilist')
        make_and_save_wikilist()
