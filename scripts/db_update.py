# author: https://github.com/vladiscripts
from scripts.db_models import PagesWithSfn, ErrRef, PageWithWarning, Timecheck, Session
from scripts import wiki_db
from scripts import logger


class UpdateDB:

    def listpages(self):
        # обновить список страниц, имеющих установленный шаблон
        self.reload_listpages_have_WarningTpl()

        # обновить список страниц, имеющих шаблоны типа {{sfn}}
        self.reload_listpages_have_sfnTpl()

        # очистка метки проверки неучтенных шаблонов
        # self.query_transcludes_any_tpl(('Citation', 'Cite'))
        # self.query_transcludes_any_tpl('Cite')

        # чистка PageTimecheck и Ref от записей которых нет в pages
        # не нужно с ForeignKey ondelete="CASCADE"
        # таки нужно
        self.clear_orphan_by_timecheck()
        self.clear_orphan_errrefs()

    def reload_listpages_have_WarningTpl(self):
        """Обновить список страниц имеющих установленный шаблон."""
        logger.info('reloading listpages have WarningTpl from WikiDB')
        logger.info('loading from WikiDB')
        w_pages = wiki_db.get_listpages_have_WarningTpl()
        # pickle_save_to_file('WarningTpl_update.pickle', w_pages)
        # w_pages = pickle_load_from_file('WarningTpl_update.pickle')

        with Session() as s:
            logger.info('clear PageWithWarning table')
            s.query(PageWithWarning).delete(synchronize_session='fetch')

            logger.info('Fill PageWithWarning table')
            for pid, title in w_pages:
                s.add(PageWithWarning(pid, title))
            s.commit()

    def reload_listpages_have_sfnTpl(self):
        """Загрузка списка страниц имеющих шаблоны типа {{sfn}}, и обновление ими базы данных

        Вариант: скачке только обновлений, имеющих sfn сейчас. См. git-branch `wikiDB_query_since_saved_last_run_time`.
        Проблема: не учитываются страницы у которых sfn был удалён.
        Получается, что если скачивать только обновления, надо делать два запроса:
        1. обновлений имеющих шаблон сейчас
        2. послать список всех страниц с sfn из локальной БД (~40k), и сравнив со списком всех в БД сейчас.
        Второй запрос - это тоже что просто запросить все страницы, + много усложнений.
        Вариант не имеет смысла.
        Или проверять отдельными запросами - к API и WikiDB наличие sfn на странице. Но это затратно.
        """

        logger.info('reloading listpages have sfnTpl from WikiDB')
        logger.info('loading from WikiDB')
        w_pages_with_sfns = wiki_db.get_listpages_have_sfnTpl()  # long query ~45000 rows
        # pickle_save_to_file('wiki_sfnTpl_update.pickle', w_pages_with_sfns)
        # w_pages_with_sfns = pickle_load_from_file('wiki_sfnTpl_update.pickle')

        # db_pages = self.db_session.query(PageWithSfn.page_id, PageWithSfn.title, Timecheck.timecheck) \
        #     .outerjoin(Timecheck, PageWithSfn.page_id == Timecheck.page_id).all()
        with Session() as s:
            db_pages = s.query(PagesWithSfn).all()

            # чистка PageWithSfn
            self.clear_orphan_sfnpages(w_pages_with_sfns, db_pages, s)

            # upsert
            logger.info('Fill PageWithSfn table')
            for page_id, title, timelastedit in w_pages_with_sfns:
                s.merge(PagesWithSfn(page_id, title, timelastedit))
            s.commit()

        # -----------

        # слишком долгая операция
        # for page_id, title, timelastedit in w_pages_with_sfns:
        #     for db in db_pages:
        #         if page_id == db.page_id:
        #             if int(timelastedit) >= int(db.timecheck) or title.decode("utf-8") != db.title:
        #                 self.db_session.merge(PageWithSfn(page_id, self.byte2utf(title), int(timelastedit)))
        #             break

        # очистка и перезаливка таблицы
        # не подходит - если удалять все, то параметр ForeignKey ondelete="CASCADE" удалит и все проверки
        # if len(w_pages_with_sfns) > 10000:  # 10000 иногда возвращается обрезанный результат
        #     self.db_session.query(PageWithSfn).delete()
        # w_pages_with_sfns = [PageWithSfn(id, self.byte2utf(title), int(timelastedit))
        #                      for id, title, timelastedit in w_pages_with_sfns]
        # self.db_session.bulk_save_objects(w_pages_with_sfns)
        # long query
        # self.s.commit()

    def clear_orphan_sfnpages(self, w_pages_with_sfns, db_pages, s):
        logger.info('Drop_orphan_sfnpages')
        db_pages_ids = {p.page_id for p in db_pages}
        w_pages_ids = {page_id for page_id, title, timelastedit in w_pages_with_sfns}
        delta = tuple(db_pages_ids - w_pages_ids)
        if delta:
            share = 100
            chunks = [delta[i:i + share] for i in range(0, len(delta), share)]
            for chunk in chunks:
                s.query(PagesWithSfn).filter(PagesWithSfn.page_id.in_(chunk)).delete(synchronize_session='fetch')
                s.commit()

    def clear_orphan_by_timecheck(self):
        """Если в pages нет записи о статье, то удалить ее строки из timecheck"""
        logger.info('Drop_orphan_by_timecheck')
        with Session() as s:
            pages = s.query(Timecheck.page_id).outerjoin(PagesWithSfn).filter(PagesWithSfn.page_id.is_(None)).all()
            for p in pages:
                s.query(Timecheck).filter(Timecheck.page_id == p.page_id).delete(synchronize_session='fetch')
            s.commit()

    def clear_orphan_errrefs(self):
        logger.info('Drop_refs_of_changed_pages')
        with Session() as s:
            pages = (p.page_id for p in s.query(ErrRef.page_id).outerjoin(PagesWithSfn)
            .filter(PagesWithSfn.page_id.is_(None)).all())
            s.query(ErrRef).filter(ErrRef.page_id.in_(pages)).delete(synchronize_session='fetch')
            s.commit()

    def clear_timechecks_of_erropages(self):
        logger.info('Drop_timechecks_of_erropages')
        with Session() as s:
            # pages = s.query(ErrRef.page_id).all()
            # for p in pages:
            #     s.query(Timecheck).filter(Timecheck.page_id == p.page_id).delete(synchronize_session='fetch')
            pages = (p.page_id for p in s.query(ErrRef.page_id).all())
            s.query(Timecheck).filter(Timecheck.page_id.in_(pages)).delete(synchronize_session='fetch')
            s.commit()

    # Helpers
    def clear_check_pages_with_warnings(self):
        """Удаление метки проверки у страниц имеющих warning-шаблон."""
        with Session() as s:
            pages = s.query(PageWithWarning.page_id).all()
            for p in pages:
                s.query(Timecheck).filter(Timecheck.page_id == p.page_id).delete(synchronize_session='fetch')
            s.commit()

    def drop_all_check_pages(self):
        """Очистка таблицы Timecheck: удаление метки проверки у всех страниц"""
        with Session() as s:
            s.query(Timecheck).delete()
            s.commit()

    def drop_all_refs(self):
        """Очистка таблицы Refs"""
        with Session() as s:
            s.query(ErrRef).delete()
            s.commit()
