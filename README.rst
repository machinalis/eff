Dependencies
============
* django-profiles
* mysqldb (if you use DotProject as source)
* south
* dateutil
* relatorio
* python-yaml
* python-pycha 

All of these are in the pip-requires file, you can install them by running::
    
    pip install -r pip-requires.txt

Install Procedure
=================
Beware, this does not work with SQlite engine, since drop columns is not suuuported and therefore south fails.

Configure DB
------------
Configure settings.py: (or you can setup local_settings.py)::

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

DotProject
----------
If you use a DotProject source, add the credentials to mysql in settings.py::

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
When a client change his data, eff send mail to/from.

Add this variables in local_settings.py to configure from/to::

    # When a client user change, send mail from
    CLIENT_CHANGE_FROM = 'from@domain.com'
    
    # When a client user change, send mail to
    CLIENT_CHANGE_RECIPIENT = (
        'your_email@domain.com',
        'another_email@domain.com',
    )
    
Change template for client change email
---------------------------------------
If you want change the email template of client change edit the following files:

* eff_site/templates/client_changed_subject.txt
* eff_site/templates/client_changed_message.txt 

Load defaults Handles
---------------------
When you run syncdb (or migrate if you have instaled south) the
following default Handles (email, twitter, skype, phone number, mobile, linkedin)
are loaded.

Weekly reports to users
-----------------------
Eff can send reports by emails weekly to users not clients and they have checked this opcion in his accounts, for that you have to configure a cron schedule in the weekday you want to send emails that excecute eff_site/scripts/send_report.py.

You have to configure this script before to use, editing eff_site/scripts/send_report.py:

Weekday emails sent by default is set to 0 (Monday), if cron calls the script on a day other than the set, are not going to send the mails::

 # Set the day of a week to send emails
 SEND_DAY = 0

Set the domain of you eff instance::

 # URL of eff_site instance
 DOMAIN = 'http://example.com'

If you want run eff in developer enviroment::

 # URL of eff_site instance
 DOMAIN = 'http://localhost:8000'
 
To customize the email template you need to edit the following files:

* eff_site/templates/previous_week_report_message.txt
* eff_site/templates/previous_week_report_subject.txt


Optional
--------
This options is for test sending mails::

    # Config Email for testing
    EMAIL_HOST = 'localhost'
    EMAIL_PORT = 1025

Sources
=======

* See scripts/config.py
