#!/usr/bin/env python3
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
# Запись списков и установка шаблонов в wiki
#
import os
from settings import *

python_and_path = r'python $PWBPATH/pwb.py'
# python_and_path = r'python scripts/'
pwb_cfg = r'-dir:~/.pywikibot/'
family = 'wikipedia'
user = 'TextworkerBot'


def posting_list():
    """Постинг списков с ошибками, из них сниппеты включаются (transcluding) в страницы."""
    sim = '-simulate' if do_post_wikilist_simulate else ''  # "-simulate" параметр для тестирования записи pwb
    params = [
        '-file:%s.txt' % filename_wikilists,
        '-begin:"%s"' % marker_page_start, '-end:"%s"' % marker_page_end, '-notitle',
        '-summary:"обновление списка"',
        '-pt:1', pwb_cfg, '-family:' + family, '-user:' + user,
        '-force', sim,
    ]
    command = '%s pagefromfile %s' % (python_and_path, ' '.join(params))
    print(command)
    os.system(command)


def posting_template():
    """Простановка в статьях шаблона про ошибки"""
    sim = '-simulate' if do_post_template_simulate else ''
    excepts = [
        # warning_tpl_regexp,
        "[Рр]едактирую", "[Ss]ubst:L", "[Ii]n-?use(-by)?", "[Pp]rocess(ing)?",
        "[Пп]равлю", "[Пп]еревожу", "[Пп]ерерабатываю", "[Сс]татья редактируется", "[Вв]икифицирую", ]
    params = [
        '-file:' + filename_listpages_errref_where_no_yet_warning_tpl,
        '-text:"{{%s}}"' % warning_tpl_name,
        '-except:"\{\{([Шш]аблон:)?(%s)\s*[|}]"' % '|'.join(excepts),
        '-summary:"+шаблон: некорректные викиссылки в сносках"',
        '-pt:1', pwb_cfg, '-family:' + family, '-user:' + user,
        '-always', sim,
    ]
    command = '%s add_text %s' % (python_and_path, ' '.join(params))
    print(command)
    os.system(command)


def remove_template():
    """Удаление шаблона из статей"""
    sim = '-simulate' if do_remove_template_simulate else ''
    params = [
        '-regex "' + warning_tpl_regexp + '.*?}}" ""', '-nocase', '-dotall',
        '-file:' + filename_list_to_remove_warning_tpl, '-ns:0',
        '-summary:"-шаблон: ошибочных викиссылок в сносках не найдено"',
        '-pt:1', pwb_cfg, '-family:' + family, '-user:' + user,
        '-always', sim,
    ]
    command = '%s replace %s' % (python_and_path, ' '.join(params))
    print(command)
    os.system(command)
