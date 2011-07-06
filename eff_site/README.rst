=======
Install
=======

- Add data base credentials here:

  * If you are going to use a DotProject source:
    sitio/scripts/dotproject.py
    class Machinalis(DotProject):
        ...
        DB = ''
        DB_USER = ''
        PASSWD = ''
        ...

  * sitio/settings.py
   DATABASE_NAME = ''           # Or path to database file if using sqlite3.
   DATABASE_USER = ''           # Not used with sqlite3.
   DATABASE_PASSWORD = ''          # Not used with sqlite3.

   SECRET_KEY = ''

  * For Jira source of logs you should add it in the source when you create it in the admin


========================
Data migration to Eff
========================

Requirements for the creation of a migration script from a given source to Eff
===============================================================================

- Create a script in the eff_site/scripts folder (i.e. souceX.py), the script must include 
  a global function named fetch_all with the following features:
  
  :Parameters: 
  
  1. source: a eff_site.eff._models.external_source.ExternalSource object (a source that exists in the DB)
  2. client: a eff_site.eff._models.client.Client object (a client that exists in the DB)
  3. author: a str object that will be used as user identifier for the log dump imported to the system. 
  4. from_date: a datetime.datetime object corresponding to the date of the beginning of the logs to be imported.
  5. to_date: a datetime.datetime object corresponding to the date of the end of the logs to be imported.
  6. _file: a file descriptor, it will be used to write the logs as they are fetched from the external source prior to the import process.

  :Required functionality (IMPORTANT): The core functionality expected here is the retrieval of the logs from a given source and the utilization of the eff_site.eff.utils.EffCsvWriter class on _file to generate the csv propperly formatted for eff to import it.

- Apend the relation with the external source to the EXT_SRC_ASSOC dictionary in eff_site/scripts/config.py .
  For instance, if our script is named "sourcex.py" the "'SourceX' : 'sourcex'" key/value pair should be added to the aforementioned dictionary.

Migrating data from an external source to Eff
===================================================

Having created the migration script, as described in the previous section, do the following to perform a migration from a given external source X:
We assume an instance of ExternalSource with "SourceX" as name attribute, just like our previous example, between two given dates (for instance between july the 1st and july the 31th of 2010) we must run eff_site/scripts/fetch_all.py as follows:

$ python fetch_all.py SourceX 20100701 20100731

