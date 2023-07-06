# scanner_broken_refs_anchors
Бот для Википедии, помечающий статьи со сломанными викиссылками в сносках, шаблоном-предупреждением, с указанием этих сносок.  Ищет по статьям, включающим шаблоны типа {{sfn}}.

**English description**:

Scanner of all pages of russian Wikipedia for broken footnotes. Marking this errors by the widget on this pages.
* Uses: Wikipedia API, MySql DB of the tool on server side via SQLAlchemy, framework Pywikibot.
* Works on tools.wmlabs.org by schedule in `crontab -e`.
* Config file: `settings.py`. And there must be data to access the wiki database in your `~/.pywikibot/user-config.py`.
* Run scripts: `scanner.py`, `post_to_wiki.py`.
