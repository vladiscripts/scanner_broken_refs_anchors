# scanner_broken_refs_anchors
Wiki: Бот, помечающий статьи со сломанными викиссылками в сносках, шаблоном-предупреждением, с указанием этих сносок.  Ищет по статьям, включающим шаблоны типа {{sfn}}. / Запуск: broken_ref_anchors.py, конфиг: config.py

Scanner of all pages of russian Wikipedia for broken footnotes. Marking this errors by the widget on this pages.

Uses: WikiAPI, Sqlite via SQLAlchemy (ORM), framework Pywikibot. 
Works on tools.wmlabs.org by shredule.

В папке с ботом необходимо создать файл passwords.py,  с содержимым для доступа к MySQL на tools.wmflabs.org:
wdb_user = "username"
wdb_pw = "password"
