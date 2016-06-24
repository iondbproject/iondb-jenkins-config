import os
import stat
import subprocess
import glob
import sys
import logging
import argparse

import configuration

sys.path.append('helper_files/')
import helper_functions
import doxygen_adapter

logger = logging.getLogger(__name__)
logger.addHandler(configuration.pc_logger)
logger.addHandler(configuration.console_logger)

parser = argparse.ArgumentParser()
parser.add_argument("-r", "--rapid", action='store_true',
                    help="Whether or not to do a rapid build. (Disables many slow profilers)")
p_args = parser.parse_args()

arguments = {'stdout': subprocess.PIPE, 'stderr': subprocess.STDOUT, 'universal_newlines': True}

# Convert coverage information
command = ['gcovr', '--branches', '--xml', '-o', os.path.join(configuration.pc_output_path, 'gcovr.xml')]
proc = subprocess.Popen(command, **arguments)
helper_functions.process_output_stream(proc, logging.INFO)

command = ['gcovr', '--branches', '--html', '--html-details',
		   '-o', os.path.join(configuration.pc_output_path, 'gcovr-report.html')]
proc = subprocess.Popen(command, **arguments)
helper_functions.process_output_stream(proc, logging.INFO)

# Build Doxygen
iondb_doxy_path = os.path.join(configuration.project_path,'documentation/doxygen/iondb_template')
command = ['doxygen', 'iondb_template']
if p_args.rapid:
	# If we're a rapid build, we skip all graph generation
	rapid_doxy_path = os.path.join(configuration.project_path,'documentation/doxygen/rapid_template')
	with open(iondb_doxy_path, 'r') as doxy_temp, open(rapid_doxy_path, 'w') as rapid_temp:
		doxygen_adapter.doxy_adapt(doxy_temp, rapid_temp)

	command = ['doxygen', 'rapid_template']

with open(os.path.join(configuration.pc_output_path, 'doxygen.log'), 'w') as err:
	proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=err, universal_newlines=True,
							cwd=os.path.join(configuration.project_path, 'documentation/doxygen'))
	helper_functions.process_output_stream(proc, logging.INFO)

# Run Cppcheck
command = ['cppcheck', '--enable=all', '--inconclusive', '--xml', '--xml-version=2',
		   os.path.join(configuration.project_path, 'src')]
with open(os.path.join(configuration.pc_output_path, 'cppcheck.xml'), 'w') as err:
	proc = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=err, universal_newlines=True)
	helper_functions.process_output_stream(proc, logging.INFO)

# Run Dr. Memory
try:
	os.mkdir(os.path.join(configuration.pc_output_path, 'drmemory'))
except OSError:
	logger.exception()

executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
for filename in glob.glob(os.path.join(configuration.pc_build_path, 'bin', 'test_*')):
	if os.path.isfile(filename):
		st = os.stat(filename)
		mode = st.st_mode
		if mode & executable:
			command	= ['drmemory', '-logdir', os.path.join(configuration.pc_output_path, 'drmemory'), '--', filename]
			proc = subprocess.Popen(command, **arguments)
			helper_functions.process_output_stream(proc, logging.INFO)

# Run Massif
try:
	os.mkdir(os.path.join(configuration.pc_output_path, 'massif'))
except OSError:
	logger.exception()

executable = stat.S_IEXEC | stat.S_IXGRP | stat.S_IXOTH
for filename in glob.glob(os.path.join(configuration.pc_build_path, 'bin', 'test_*')):
	if os.path.isfile(filename):
		st = os.stat(filename)
		mode = st.st_mode
		if mode & executable:
			command = ['valgrind', '--tool=massif', '--stacks=yes', '--heap=yes',
					   '--massif-out-file=' + os.path.join(configuration.pc_output_path, 'massif', os.path.basename(filename)),
					   filename]
			proc = subprocess.Popen(command, **arguments)
			helper_functions.process_output_stream(proc, logging.INFO)
