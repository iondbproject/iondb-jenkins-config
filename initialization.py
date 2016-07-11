import logging
import os
import shutil
import subprocess
import sys
import argparse

import configuration

sys.path.append('helper_files/')
import helper_functions

logger = logging.getLogger(__name__)
logger.addHandler(configuration.console_logger)

parser = argparse.ArgumentParser()
parser.add_argument("branch", nargs="?", default="development", help="Branch target to clone.")
p_args = parser.parse_args()

#--------------
# Clone IonDB
#--------------

logger.info('Cloning IonTable, targeting branch ' + p_args.branch)

try:
	shutil.rmtree('iontable/')
except OSError:
	logger.warning('Failed to remove IonDB project folder. It may not have existed.')

arguments = {'stdout': subprocess.PIPE, 'stderr': subprocess.STDOUT, 'universal_newlines': True}

proc = subprocess.Popen(['git', 'clone', '--depth=1', 'https://github.com/iondbproject/iontable.git', 'iontable',
						 '--recursive', '-b', p_args.branch], **arguments)
helper_functions.process_output_stream(proc)
if proc.returncode != 0:
	logger.error('Failed to clone IonTable repository')
	sys.exit(1)

proc = subprocess.Popen(['git', 'submodule', 'update', '--init', '--remote'], **arguments)
helper_functions.process_output_stream(proc)
if proc.returncode != 0:
	logger.error('Failed to initialize submodule')
	sys.exit(1)

#------------------------------
# Create log output folders
#------------------------------

try:
	os.makedirs(configuration.pc_build_path)
except OSError:
	logger.warning('Failed to create pc output directory. It probably already exits.')

try:
	os.makedirs(configuration.pc_build_path)
except OSError:
	logger.warning('Failed to create device output directory. It probably already exits.')

logger.info('Successfully cloned IonDB')
