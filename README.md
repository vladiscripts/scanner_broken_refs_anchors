# scanner_broken_refs_anchors
Бот для Википедии, помечающий статьи со сломанными викиссылками в сносках, шаблоном-предупреждением, с указанием этих сносок.  Ищет по статьям, включающим шаблоны типа {{sfn}}.

**English description**:

Scanner of all pages of russian Wikipedia for broken footnotes. Marking this errors by the widget on this pages.
* Uses: Wikipedia API, Sqlite via SQLAlchemy (ORM), framework Pywikibot, asyncio, aiohttp.
* Works on tools.wmlabs.org by schedule in `crontab -e`.
* In bot's folder need to create passwords.py with the 2 lines:
`wdb_user = "username"`, `wdb_pw = "password"`. There to set your credentials for access to MySQL on tools.wmflabs.org.  
* Config file: config.py. 
* Run file: broken_ref_anchors.py.
