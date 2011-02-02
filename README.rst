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


 * if you use a DotProject source, add the credentials to mysql in settings.py:

   DOTPROJECT_DB_NAME = ''
   DOTPROJECT_DB_USER = ''
   DOTPROJECT_DB_PASSWD = ''
   DOTPROJECT_DB_HOST = 'localhost'
   DOTPROJECT_DB_PORT = 3306
   DOTPROJECT_DB_CHARSET = 'latin1'

 * comment in settings.py the AUTH_PROFILE_MODULE = 'eff.userprofile' line

 * python manage.py syncdb
 
 * python manage.py migrate

 * then uncomment the line AUTH_PROFILE_MODULE...

Sources
=======

 See scripts/config.py
