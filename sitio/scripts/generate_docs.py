#!/usr/bin/env python
# Copyright 2011 Machinalis: http://www.machinalis.com/
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


import commands
import os
import sys

MODULES = ['eff', 'scripts']

if __name__ == "__main__":
    project_path = os.sep.join(os.path.abspath(__file__).split(os.sep)[:-2])
    config_path = os.path.join(project_path, "scripts", "epydoc.config")
    if not os.path.exists(config_path):
        print >>sys.stderr, "Cannot find epydoc configuration file '%s'" % config_path
        sys.exit(1)
    os.putenv("PYTHONPATH", ".:%s" % project_path)
    os.putenv("DJANGO_SETTINGS_MODULE", "settings")
    api_path = os.path.join(project_path, "docs", "api")
    if not os.path.exists(api_path):
        os.makedirs(api_path)
    files = [os.path.join(project_path, 'settings.py'), os.path.join(project_path, 'urls.py')]
    for m in MODULES:
        mp = os.path.join(project_path, m)
        for dirpath, dirnames, filenames in os.walk(mp):
            files.extend(["'%s'" % os.path.join(dirpath, f) for f in filenames if f.endswith(".py")])
    files_joined = " ".join(files)
    cmd = "epydoc --name=Eff --config='%s' --output='%s' %s" % (config_path, api_path, files_joined, )
    output = commands.getoutput(cmd)
    for line in output.split("\n"):
        if line.startswith("| "):
            print line[2:]
