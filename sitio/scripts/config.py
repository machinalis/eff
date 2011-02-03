# -*- coding: utf-8 -*-
# Copyright 2009 - 2011 Machinalis: http://www.machinalis.com/
#
# This file is part of Eff.
#
# Eff is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Eff is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Eff.  If not, see <http://www.gnu.org/licenses/>.


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
