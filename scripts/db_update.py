# author: https://github.com/vladiscripts
#
from scripts.logger import logger
from scripts.db_models import PageWithSfn, ErrRef, PageWithWarning, Timecheck, Session, db_session as s
from scripts import wiki_db
from vladi_helpers.file_helpers import pickle_save_to_file, pickle_load_from_file


class UpdateDB:
    def __init__(self):
        self.s = Session()

    # def __del__(self):
    #     Session.remove()

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
        # w_pages = wiki_db.get_listpages_have_WarningTpl()
        # w_pages = tuple(w_pages)
        # pickle_save_to_file('WarningTpl.pickle', w_pages)
        w_pages = pickle_load_from_file('WarningTpl.pickle')

        self.s.query(PageWithWarning).delete()
        for pid, title in w_pages:
            self.s.add(PageWithWarning(pid, title))
        self.s.commit()

    def reload_listpages_have_sfnTpl(self):
        """Загрузка списка страниц имеющих шаблоны типа {{sfn}}, и обновление ими базы данных"""
        # w_pages_with_sfns = wiki_db.get_listpages_have_sfnTpl()  # long query ~45000 rows
        # w_pages_with_sfns = tuple(w_pages_with_sfns)
        # pickle_save_to_file('wiki_sfnTpl.pickle', w_pages_with_sfns)
        w_pages_with_sfns = pickle_load_from_file('wiki_sfnTpl.pickle')

        # db_pages = self.db_session.query(PageWithSfn.page_id, PageWithSfn.title, Timecheck.timecheck) \
        #     .outerjoin(Timecheck, PageWithSfn.page_id == Timecheck.page_id).all()
        db_pages = self.s.query(PageWithSfn).all()

        # чистка PageWithSfn
        self.clear_orphan_sfnpages(w_pages_with_sfns, db_pages)

        # upsert
        logger.info('Updating of timelastedits in PageWithSfn table')
        for page_id, title, timelastedit in w_pages_with_sfns:
            # self.s.merge(PageWithSfn(page_id, title, timelastedit))
            pass
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
        self.s.commit()

    def clear_orphan_sfnpages(self, w_pages_with_sfns, db_pages):
        logger.info('Drop_orphan_sfnpages')
        db_pages_ids = {p.page_id for p in db_pages}
        w_pages_ids = {page_id for page_id, title, timelastedit in w_pages_with_sfns}
        delta = tuple(db_pages_ids - w_pages_ids)
        if delta:
            share = 100
            chunks = [delta[i:i + share] for i in range(0, len(delta), share)]
            for chunk in chunks:
                self.s.query(PageWithSfn).filter(PageWithSfn.page_id.in_(chunk)).delete(synchronize_session='fetch')
                self.s.commit()

    def clear_orphan_by_timecheck(self):
        """Если в pages нет записи о статье, то удалить ее строки из timecheck"""
        logger.info('Drop_orphan_by_timecheck')
        pages = self.s.query(Timecheck.page_id).outerjoin(PageWithSfn).filter(PageWithSfn.page_id.is_(None)).all()
        for p in pages:
            c = self.s.query(Timecheck).filter(Timecheck.page_id == p.page_id).delete()
        self.s.commit()

    def clear_orphan_errrefs(self):
        logger.info('Drop_refs_of_changed_pages')
        # pages = Session.query(ErrRef.page_id).outerjoin(PageWithSfn).filter(PageWithSfn.page_id.is_(None)).all()
        # for p in pages:  # DELETE do not work with JOIN
        #     Session.query(ErrRef).filter(ErrRef.page_id == p.page_id).delete(synchronize_session='fetch')
        pages = (p.page_id for p in self.s.query(ErrRef.page_id).outerjoin(PageWithSfn)
            .filter(PageWithSfn.page_id.is_(None)).all())
        c = self.s.query(ErrRef).filter(ErrRef.page_id.in_(pages)).delete(synchronize_session='fetch')
        self.s.commit()

    def clear_timechecks_of_erropages(self):
        logger.info('Drop_timechecks_of_erropages')
        # pages = self.db_session.query(ErrRef.page_id).all()
        # for p in pages:
        #     self.db_session.query(Timecheck).filter(Timecheck.page_id == p.page_id).delete(synchronize_session='fetch')
        pages = (p.page_id for p in self.s.query(ErrRef.page_id).all())
        self.s.query(Timecheck).filter(Timecheck.page_id.in_(pages)).delete(synchronize_session='fetch')
        self.s.commit()

    # Helpers
    def clear_check_pages_with_warnings(self):
        """Удаление метки проверки у страниц имеющих warning-шаблон."""
        pages = self.s.query(PageWithWarning.page_id).all()
        for p in pages:
            self.s.query(Timecheck).filter(Timecheck.page_id == p.page_id).delete(synchronize_session='fetch')
        self.s.commit()

    def drop_all_check_pages(self):
        """Очистка таблицы Timecheck: удаление метки проверки у всех страниц"""
        self.s.query(Timecheck).delete()
        self.s.commit()

    def drop_all_refs(self):
        """Очистка таблицы Refs"""
        self.s.query(ErrRef).delete()
        self.s.commit()
