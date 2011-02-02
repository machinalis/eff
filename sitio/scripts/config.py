# -*- coding: utf-8 -*-

# Association between external source name and external source fetcher 
# (must contain a specific fetch_all global function)
# These should match the name of the source you create
# If you create a source Dotproject, name it Dotproject so
# you use dotproject.py to load data

EXT_SRC_ASSOC = {
    'Dotproject' : 'dotproject',
    'Tutos' : 'tutos',
    'Jira' : 'jira',
    }
