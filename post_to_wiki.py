#!/usr/bin/env python3
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
# Запись списков и установка шаблонов в wiki
#
import os
import shlex, subprocess
from datetime import datetime
from settings import *

python_and_path = 'python %s/pwb.py' % os.getenv('PWBPATH')
family = 'wikipedia'
user = 'TextworkerBot'
pwb_cfg = '-dir:~/.pywikibot/'
args_base = [f'-family:{family}', '-lang:ru', f'-user:{user}', '-pt:1', pwb_cfg]


# ToDo:
# чтобы опять не писались в ВП предупреждения, на основе старых статусов проверки,
# - можно проверять код завершения предыдущего скрипта на ошибку,
# - переименовывать файлы со списками после их обработки

def run(command, filename):
    if not os.path.isfile(filename):
        raise Exception(f'No file "{filename}"')
    # os.system(command)
    code = subprocess.Popen(shlex.split(command)).wait()
    # ToDo код завершения всегда == 0, ошибка не проверятся.
    # ToDo Хотя это может это только если сам pwb не закрылся по Exception? Сейчас нет времени на тесты.
    # ToDo Если же == 0 в любом случае, то надо открывать вопрос на Phabricator
    assert code == 0, f'posting subprocess exited with status {code}'
    # p = subprocess.Popen(shlex.split(command), stdout=subprocess.PIPE, stderr=subprocess.PIPE, encoding='utf-8')  # .wait()
    # stdout, stderr = p.communicate()
    # if p.returncode != 0:
    #     raise Exception('snmpget exited with status %r: %r' % (p.returncode, stderr))
    # errcode = os.system(command)
    os.rename(filename, f'~{filename}')


def posting_wikilist():
    """Постинг списков с ошибками, из них сниппеты включаются (transcluding) в страницы."""
    args = [
        '-file:%s' % filename_wikilists,
        '-begin:"%s"' % marker_page_start, '-end:"%s"' % marker_page_end, '-notitle',
        '-summary:"обновление списка"',
        '-force',
    ]
    args.extend(args_base)
    if do_post_wikilist_simulate: args.append('-simulate')  # "-simulate" параметр для тестирования записи pwb
    command = '%s pagefromfile %s' % (python_and_path, ' '.join(args))
    run(command, filename_wikilists)


# todo: заменить {{PAGENAME}} на {{PAGEID}}
def posting_template():
    """Простановка в статьях шаблона про ошибки"""
    excepts = [
        # warning_tpl_regexp,
        "[Рр]едактирую", "[Ss]ubst:L", "[Ii]n-?use(-by)?", "[Pp]rocess(ing)?",
        "[Пп]равлю", "[Пп]еревожу", "[Пп]ерерабатываю", "[Сс]татья редактируется", "[Вв]икифицирую", ]
    args = [
        '-file:' + filename_listpages_errref_where_no_yet_warning_tpl,
        '-text:"{{%s}}"' % warning_tpl_name,
        '-grepnot:"\{\{([Шш]аблон:)?(%s)\s*[|}]"' % '|'.join(excepts),
        '-summary:"+шаблон: некорректные викиссылки в сносках"',
        '-always',
    ]
    args.extend(args_base)
    if do_post_template_simulate: args.append('-simulate')
    command = '%s add_text %s' % (python_and_path, ' '.join(args))
    run(command, filename_listpages_errref_where_no_yet_warning_tpl)


def remove_template():
    """Удаление шаблона из статей"""
    args = [
        '-regex "' + warning_tpl_regexp + '.*?}}" ""', '-nocase', '-dotall',
        '-file:' + filename_list_to_remove_warning_tpl, '-ns:0',
        '-summary:"-шаблон: не найдено ошибочных викиссылок в сносках"',
        '-always',
    ]
    args.extend(args_base)
    if do_remove_template_simulate: args.append('-simulate')
    command = '%s replace %s' % (python_and_path, ' '.join(args))
    run(command, filename_list_to_remove_warning_tpl)


def login():
    command = f'{python_and_path} login {" ".join(args_base)}'
    code = subprocess.Popen(shlex.split(command)).wait()
    assert code == 0


if __name__ == '__main__':

    # Постинг списков и установка шаблонов в wiki
    # do_posts_simulate = True
    if do_posts_simulate:
        do_post_wikilist_simulate = do_post_template_simulate = do_remove_template_simulate = True

    # to tests
    # posting_wikilist()
    # posting_template()

    if do_post_to_wiki:
        t = datetime.now()
        print(f'{t} Start posting')
        login()
        if do_post_wikilist:
            posting_wikilist()
        if do_post_template:
            posting_template()
        if do_remove_template:
            remove_template()
