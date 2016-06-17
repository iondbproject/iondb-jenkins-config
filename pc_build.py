#!/usr/bin/env python3
import logging
import subprocess
import sys

import configuration

sys.path.append('helper_files/')
import helper_functions

logger = logging.getLogger(__name__)
logger.addHandler(configuration.pc_logger)
logger.addHandler(configuration.console_logger)


logger.info('Starting pc build')

proc = subprocess.Popen(['cmake', '-DCOVERAGE_TESTING=ON', configuration.project_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
						universal_newlines=True, cwd=configuration.pc_build_path)
helper_functions.process_output_stream(proc)

if proc.returncode != 0:
	logger.error('Generating Makefiles with CMake failed')
	sys.exit(0)

proc = subprocess.Popen(['make', 'all'], cwd=configuration.pc_build_path, stdout=subprocess.PIPE,
						stderr=subprocess.STDOUT, universal_newlines=True)
helper_functions.process_output_stream(proc)

if proc.returncode != 0:
	logger.error('Some or all tests failed to compile')
	sys.exit(0)

logger.info('Build process finished')
