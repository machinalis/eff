Dependencies
============

    * django-profiles
    * mysqldb (if you use DotProject as source)
    * south
    * dateutil
    * relatorio
    * python-yaml
    * python-pycha 

    All of these are in the pip-requires file, you can install them by running:
    * pip install -r pip-requires.txt

Install Procedure
================

 Beware, this does not work with SQlite engine, since drop columns is not suuuported
 and therefore south fails.

 * configure settings.py: (or you can setup local_settings.py)

    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.', # Add 'postgresql_psycopg2', 'postgresql', 'mysql', 'sqlite3' or 'oracle'.
            'NAME': '',                      # Or path to database file if using sqlite3.
            'USER': '',                      # Not used with sqlite3.
            'PASSWORD': '',                  # Not used with sqlite3.
            'HOST': '',                      # Set to empty string for localhost. Not used with sqlite3.
            'PORT': '',                      # Set to empty string for default. Not used with sqlite3.
        }
    }

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
 
Configuring email settings
--------------------------

When a client change his data, eff send mail to/from

# When a client user change, send mail from
CLIENT_CHANGE_FROM = 'from@domain.com'

# When a client user change, send mail to
CLIENT_CHANGE_RECIPIENT = (
    'your_email@domain.com',
)

Change template for client change email
---------------------------------------

If you want change the email template of client change, edit:

 * eff_site/templates/client_changed_subject.txt
 * eff_site/templates/client_changed_message.txt 

Optional
--------

This options is for test sending mails
# Config Email for testing
EMAIL_HOST = 'localhost'
EMAIL_PORT = 1025


Sources
=======

 See scripts/config.py
