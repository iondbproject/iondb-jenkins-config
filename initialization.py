import logging
import os
import shutil
import subprocess
import sys

import configuration

sys.path.append('helper_files/')
import helper_functions

logger = logging.getLogger(__name__)
logger.addHandler(configuration.device_logger)
logger.addHandler(configuration.console_logger)

#--------------
# Clone IonDB
#--------------

logger.info('Cloning IonDB')

try:
	shutil.rmtree('iondb/')
except OSError:
	logger.exception('Failed to remove IonDB project folder. It may not have existed.')

arguments = {'stdout': subprocess.PIPE, 'stderr': subprocess.STDOUT, 'universal_newlines': True}

proc = subprocess.Popen(['git', 'clone', '--depth=1', 'https://github.com/iondbproject/iondb.git', 'iondb',
						 '--recursive', '-b', 'development'], **arguments)
helper_functions.process_output_stream(proc, configuration.output_build)
if proc.returncode != 0:
	logger.error('Failed to clone IonDB repository')
	sys.exit(1)

proc = subprocess.Popen(['git', 'submodule', 'init'], **arguments)
helper_functions.process_output_stream(proc, configuration.output_build)
if proc.returncode != 0:
	logger.error('Failed to initialize submodule')
	sys.exit(1)

proc = subprocess.Popen(['git', 'submodule', 'update', '--remote'], **arguments)
helper_functions.process_output_stream(proc, configuration.output_build)
if proc.returncode != 0:
	logger.error('Failed to initialize submodule')
	sys.exit(1)

#------------------------------
# Create log output folders
#------------------------------

try:
	os.makedirs(configuration.pc_output)
	os.makedirs(os.path.join(configuration.pc_output + '/build'))
except OSError:
	logger.exception('Failed to create pc output directory. It probably already exits.')

try:
	os.makedirs(configuration.device_output)
	os.makedirs(os.path.join(configuration.pc_output + '/build'))
except OSError:
	logger.exception('Failed to create device output directory. It probably already exits.')
