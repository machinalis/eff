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
 
Other configurations
====================

Sending email when a client user changes
----------------------------------------
When change a client user, the system send mail notifications.

Add this variables in local_settings.py to configure from/to::

    # When change a client user, send mail from
    CLIENT_CHANGE_FROM = 'from@domain.com'
    
    # When change a client user, send mail to. This is a tuple of all recipients
    CLIENT_CHANGE_RECIPIENT = (
        'your_email@domain.com',
        'another_email@domain.com',
    )
    
Customize the template of the user mail exchange
------------------------------------------------
If you want change the email template of client change, you need to edit the following files:

* eff_site/templates/client_changed_subject.txt
* eff_site/templates/client_changed_message.txt 

Load defaults Handles
---------------------
When you run syncdb (or migrate if you have installed south) the following default Handles are loaded:

* email
* twitter
* skype
* phone number
* mobile
* linkedin

Weekly reports to users
-----------------------
Eff can send reports by emails weekly to users not clients if they are checked this option in his settings. Your server need to call send_report.py script in the weekday you want to send emails.

You have to configure this script before to use, editing eff_site/scripts/send_report.py:

The emails are sent the day of the week defined by the variable SEND_DAY (default is set to 0 (Monday)), if your server calls the script on a day other than the set, are not going to send the mails::

 # Set the day of a week to send emails
 SEND_DAY = 0

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
