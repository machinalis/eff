Dependencies
============

    * django-profiles
    * mysqldb (if you use DotProject as source)
    * south
    * dateutil
    * relatorio
    * python-yaml
    * python-pycha 


Install Procedure
================

 * configure settings.py: (or you can setup local_settings.py)
   DATABASE_NAME = ''           # Or path to database file if using sqlite3.
   DATABASE_USER = ''           # Not used with sqlite3.
   DATABASE_PASSWORD = ''       # Not used with sqlite3.

   SECRET_KEY = ''


 * if you use a DotProject source, add the credentials to mysql database in scripts/dotproject.py
    DB = ''
    DB_USER = ''
    PASSWD = ''

 * In migration 0007_dump_migration.py 
 connection = MySQLdb.connect(db='',
                              user='',
                              passwd='',
                              host='localhost',
                              port=3306, charset = "latin1")


 * comment in settings.py the AUTH_PROFILE_MODULE = 'eff.userprofile' line

 * python manage.py syncdb
 
 * python manage.py migrate

 * then uncomment the line AUTH_PROFILE_MODULE...

Sources
=======

 See scripts/config.py
