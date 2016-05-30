#!/usr/bin/env python

import os

os.system('git clone https://github.com/iondbproject/iondb.git --recursive')
os.chdir('iondb')
os.system('git checkout linear-hash-fix')
os.system('git submodule init')
os.system('git submodule update --remote')
os.system('mkdir build')
os.chdir('build')
os.system('cmake ..')
os.system('make all')
os.chdir('bin')

for toexecute in os.listdir('.'):
        os.system(toexecute)