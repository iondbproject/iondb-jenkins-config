#!/usr/bin/env python3
import sys
import subprocess
import logging

sys.path.append('../../')
import configuration
import helper_functions

logger = logging.getLogger(__name__)
logger.addHandler(configuration.pc_logger)
logger.addHandler(configuration.console_logger)


proc = subprocess.Popen(['cmake', configuration.project_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
						universal_newlines=True)
helper_functions.process_output_stream(proc, configuration.output_build)

if proc.returncode != 0:
	print('PC build failed')
	sys.exit(1)

proc = subprocess.Popen(['make', 'all'], cwd=configuration.pc_output + '/build', stdout=subprocess.PIPE,
						stderr=subprocess.STDOUT, universal_newlines=True)
helper_functions.process_output_stream(proc, configuration.output_build)

if proc.returncode != 0:
	print('Running tests failed')
	sys.exit(1)
