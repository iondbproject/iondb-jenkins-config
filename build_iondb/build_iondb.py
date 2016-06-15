#!/usr/bin/env python

import os
import shutil

try:
    shutil.rmtree("iondb/")
except FileNotFoundError:
    print("iondb/ didn't exist. No remove.")
os.system('git clone https://github.com/iondbproject/iondb.git --recursive')
os.chdir('iondb')
os.system('git checkout coverage_planck-close')#os.system('git checkout development')
os.system('git submodule init')
os.system('git submodule update --remote')
os.system('mkdir build')
os.chdir('build')
os.system('cmake .. -DCOVERAGE_TESTING=ON')
os.system('make all')