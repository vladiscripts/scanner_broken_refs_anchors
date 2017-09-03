#!/usr/bin/env python3
# coding: utf-8
#
# author: https://github.com/vladiscripts
#
# Запись списков и установка шаблонов в wiki
#
import os
from config import *

python_and_path = r'python $PWBPATH/pwb.py'
# python_and_path = r'python scripts/'
pwb_cfg = r'-dir:~/.pywikibot/'
family = 'wikipedia'


def posting_list():
	"""Постинг списков с ошибками, из них сниппеты включаются (transcluding) в страницы."""
	sim = '-simulate' if do_post_list_simulate else ''  # "-simulate" параметр для тестирования записи pwb
	params = [
		'-file:' + filename_wikilists + '.txt',
		'-begin:"' + marker_page_start + '"', '-end:"' + marker_page_end + '"', '-notitle',
		'-summary:"обновление списка"',
		'-pt:1', pwb_cfg, '-family:' + family,
		'-force', sim,
	]	
	os.system('%s pagefromfile %s' % (python_and_path, ' '.join(params)))


def posting_template():
	"""Простановка в статьях шаблона про ошибки"""
	sim = '-simulate' if do_post_template_simulate else ''
	excepts = [
		# warning_tpl_regexp,
		"[Рр]едактирую", "[Ss]ubst:L", "[Ii]n-?use(-by)?", "[Pp]rocess(ing)?",
		"[Пп]равлю", "[Пп]еревожу", "[Пп]ерерабатываю", "[Сс]татья редактируется", "[Вв]икифицирую", ]
	params = [
		'-file:' + filename_listpages_errref_where_no_yet_warning_tpl,
		'-text:"{{' + warning_tpl_name + '}}"',
		'-except:"\{\{([Шш]аблон:)?(%s)\s*[|}]"' % '|'.join(excepts),
		'-summary:"+шаблон: некорректные викиссылки в сносках"',
		'-pt:1', pwb_cfg, '-family:' + family,
		'-always', sim,
	]
	os.system('%s add_text %s' % (python_and_path, ' '.join(params)))


def posting_template():
	"""Удаление шаблона из статей"""
	sim = '-simulate' if do_remove_template_simulate else ''
	params = [
		'-regex "' + warning_tpl_regexp + '.*?}}" ""', '-nocase', '-dotall',
		'-file:' + filename_list_to_remove_warning_tpl, '-ns:0',
		'-summary:"-шаблон: ошибочных викиссылок в сносках не найдено"',
		'-pt:1', pwb_cfg, '-family:' + family,
		'-always', sim,
	]
	os.system('%s replace %s' % (python_and_path, ' '.join(params)))


def bot_login_check():	
	os.system(python_and_path + ' login ' + pwb_cfg)
