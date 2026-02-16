# author: https://github.com/vladiscripts
from sqlalchemy import select, delete
from sqlalchemy.dialects.mysql import insert as mysql_insert

from scripts.db_models import PagesWithSfn, ErrRef, PageWithWarning, Timecheck, Session
from scripts import wiki_db
from scripts import logger, _chunked


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
        pages_with_warning_in_wiki = wiki_db.get_listpages_have_WarningTpl()
        logger.info(f'Downloaded {len(pages_with_warning_in_wiki)} records of pages with WarningTpl from WikiDB')
        # pickle_save_to_file('WarningTpl_update.pickle', pages_with_warning_in_wiki)
        # pages_with_warning_in_wiki = pickle_load_from_file('WarningTpl_update.pickle')

        with Session() as s:
            try:
                logger.info('clear PageWithWarning table')
                s.execute(delete(PageWithWarning))

                if pages_with_warning_in_wiki:
                    logger.info('Fill PageWithWarning table')
                    data = [PageWithWarning(r.page_id, r.title).as_dict() for r in pages_with_warning_in_wiki]
                    stmt = mysql_insert(PageWithWarning.__table__).values(data)
                    s.execute(stmt)
                s.commit()

            except Exception as e:
                s.rollback()
                logger.error(f"Failed to update PageWithWarning: {e}")
                raise

    def reload_listpages_have_sfnTpl(self):
        """Загрузка списка страниц имеющих шаблоны типа {{sfn}}, и обновление ими базы данных."""
        logger.info('reloading listpages have sfnTpl from WikiDB')
        logger.info('loading from WikiDB')
        pages_with_sfns_wiki = wiki_db.get_listpages_have_sfnTpl()  # long query ~126000 rows per 9-11 seconds
        logger.info(f'Downloaded {len(pages_with_sfns_wiki)} records of pages with sfnTpl from WikiDB')
        # pickle_save_to_file('wiki_sfnTpl_update.pickle', pages_with_sfns_wiki)
        # pages_with_sfns_wiki = pickle_load_from_file('wiki_sfnTpl_update.pickle')

        with Session() as s:
            # чистка PagesWithSfn
            self.clear_orphan_sfnpages(s, pages_with_sfns_wiki)

            # обновление PagesWithSfn
            upsert_data = [PagesWithSfn(r.page_id, r.title, r.timelastedit).as_dict() for r in pages_with_sfns_wiki]
            if upsert_data:
                stmt = mysql_insert(PagesWithSfn.__table__).values(upsert_data)
                stmt = stmt.on_duplicate_key_update(title=stmt.inserted.title, timelastedit=stmt.inserted.timelastedit)
                s.execute(stmt)
            s.commit()

        logger.info('reload_listpages_have_sfnTpl completed')

        # -----------

        # слишком долгая операция
        # for page_id, title, timelastedit in pages_with_sfns_wiki:
        #     for db in db_pages:
        #         if page_id == db.page_id:
        #             if int(timelastedit) >= int(db.timecheck) or title.decode("utf-8") != db.title:
        #                 self.db_session.merge(PageWithSfn(page_id, self.byte2utf(title), int(timelastedit)))
        #             break

        # очистка и перезаливка таблицы
        # не подходит - если удалять все, то параметр ForeignKey ondelete="CASCADE" удалит и все проверки
        # if len(pages_with_sfns_wiki) > 10000:  # 10000 иногда возвращается обрезанный результат
        #     self.db_session.query(PageWithSfn).delete()
        # pages_with_sfns_wiki = [PageWithSfn(id, self.byte2utf(title), int(timelastedit))
        #                      for id, title, timelastedit in pages_with_sfns_wiki]
        # self.db_session.bulk_save_objects(pages_with_sfns_wiki)
        # long query
        # self.s.commit()

    def clear_orphan_sfnpages(self, s, pages_with_sfns_wiki):
        """Синхронизация базы данных с WikiDB. Удаление из таблицы PagesWithSfn записей о страницах у которых в Википедии удалён шаблон {{sfn}}."""
        logger.info('Drop_orphan_sfnpages')
        page_ids_wiki = {r.page_id for r in pages_with_sfns_wiki}
        page_ids_db = {r.page_id for r in s.execute(select(PagesWithSfn.page_id)).fetchall()}
        to_delete = page_ids_db - page_ids_wiki
        if to_delete:
            for chunk in _chunked(to_delete, 1000):
                stmt = delete(PagesWithSfn).where(PagesWithSfn.page_id.in_(chunk))
                s.execute(stmt)

    def clear_orphan_by_timecheck(self):
        """Если в pages нет записи о статье, то удалить ее строки из timecheck"""
        logger.info('Drop_orphan_by_timecheck')
        with Session() as s:
            stmt = delete(Timecheck).where(~Timecheck.page_id.in_(select(PagesWithSfn.page_id)))
            s.execute(stmt)
            s.commit()

    def clear_orphan_errrefs(self):
        logger.info('Drop_refs_of_changed_pages')
        with Session() as s:
            stmt = delete(ErrRef).where(~ErrRef.page_id.in_(select(PagesWithSfn.page_id)))
            s.execute(stmt)
            s.commit()

    def clear_timechecks_of_erropages(self):
        logger.info('Drop_timechecks_of_erropages')
        with Session() as s:
            stmt = delete(Timecheck).where(Timecheck.page_id.in_(select(ErrRef.page_id).distinct()))
            s.execute(stmt)
            s.commit()

    def clear_check_pages_with_warnings(self):
        """Удаление метки проверки у страниц имеющих warning-шаблон."""
        with Session() as s:
            stmt = delete(Timecheck).where(Timecheck.page_id.in_(select(PageWithWarning.page_id)))
            s.execute(stmt)
            s.commit()

    def drop_all_check_pages(self):
        """Очистка таблицы Timecheck: удаление метки проверки у всех страниц"""
        with Session() as s:
            s.execute(delete(Timecheck))
            s.commit()

    def drop_all_refs(self):
        """Очистка таблицы Refs"""
        with Session() as s:
            s.execute(delete(ErrRef))
            s.commit()
