#!/usr/bin/env python3
import glob
import logging
import os.path
import subprocess
import sys

import configuration

sys.path.append('helper_files/')
import helper_functions
import planck_xunit_adapter as pxa

logger = logging.getLogger(__name__)
logger.addHandler(configuration.pc_logger)
logger.addHandler(configuration.console_logger)


logger.info('Starting test phase.')

for abstest_path in glob.glob(os.path.join(configuration.pc_build_path, 'test_*')):
	test_exec = os.path.basename(abstest_path)
	planck_outputfname = os.path.join(configuration.pc_output_path, 'planckunit_{testname}_output.txt').format(testname=test_exec)
	xunit_outputfname = os.path.join(configuration.pc_output_path, 'xunit_{testname}_output.txt').format(testname=test_exec)

	args = {'stdout': subprocess.PIPE, 'stderr': subprocess.STDOUT, 'universal_newlines': True}

	proc = subprocess.Popen(['chmod', '+x', abstest_path], **args)
	helper_functions.process_output_stream(proc)

	proc = subprocess.Popen([abstest_path, '|', 'tee', planck_outputfname], shell=True, **args)
	helper_functions.process_output_stream(proc)

	logger.info('Adapting {pl} -> {xl}...'.format(pl=planck_outputfname, xl=xunit_outputfname))
	with open(planck_outputfname, 'r+') as planck_file, open(xunit_outputfname, 'w+') as xunit_file:
		pxa.PlanckAdapter(test_exec, planck_file, xunit_file).adapt_planck_file()

logger.info('Completed test process.')
