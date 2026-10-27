import configparser
import pathlib

"""
В этом файле подключение к пользовательской БД с refs. Не путать с подключением к ruwiki БД.
https://wikitech.wikimedia.org/wiki/Help:Toolforge/Database#User_databases
При запуске на ПК перебрасывать эти подключения на разные порты.
Например, две строки в паралельных терминалах:
ssh -L 4712:ruwiki.web.db.svc.wikimedia.cloud:3306 vladi2016@login.toolforge.org -i "~/.ssh/id_rsa"
ssh -L 4716:tools.db.svc.wikimedia.cloud:3306 vladi2016@login.toolforge.org -i "~.ssh/id_rsa"

(Но обновление remote БД будет крайне медленным, отлаживать лучше с локальной БД refs.)
"""
replica = pathlib.Path.home().joinpath('replica.my.cnf')
if replica.exists():
    config = configparser.ConfigParser()
    config.read_string(replica.read_text())
    user, password = config.get('client', 'user'), config.get('client', 'password')

else:
    import os
    user, password = os.environ['USER_DB_WIKIMEDIA'].split(':')

engine_conn_str = f'mysql+pymysql://{user}:{password}@tools.db.svc.wikimedia.cloud/s53112__pagesrefs'
