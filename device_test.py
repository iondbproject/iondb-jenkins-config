#!/usr/bin/python
import logging
import os
import re
import shutil
import sys
import threading
import time
from collections import namedtuple

import configuration

sys.path.append('device_helper_files/')
from cmake_build import CMakeBuild
from arduino_boards_serial import ArduinoBoardsSerial
from make_targets import MakeTargets
import planck_serial

sys.path.append('helper_files/')
from helper_files import planck_xunit_adapter as pxa

build_data = namedtuple('build_data', ['arduino', 'dir', 'targets'])

logger = logging.getLogger(__name__)
logger.addHandler(configuration.device_logger)
logger.addHandler(configuration.console_logger)


def upload_and_read_serial(target_name, arduino_build, output_dir):
	logger.info('Running ' + target_name)
	CMakeBuild.execute_make_target(target_name, os.path.join(configuration.device_build_path, arduino_build[0].dir),
								   False)
	planck_serial.parse_serial(output_dir, arduino_build[0].arduino.port, baud_rate=configuration.baud_rate,
							   target_name=target_name, timeout=configuration.timeout)
	logger.info('Finished running ' + target_name)
	arduino_build[1] = True

logger.info('Starting test phase.')

# Note: The list of ArduinoBoards are already sorted by ID.
arduino_boards = ArduinoBoardsSerial.load_arduino_boards(os.path.join(configuration.device_output_path,
																	  'connected_arduino_boards.txt'))
arduino_board_targets = MakeTargets.load_board_make_targets(os.path.join(configuration.device_output_path,
																		 'make_board_targets.txt'))
arduino_builds = []

# Match the Arduino boards to their corresponding builds and targets
for entry in os.listdir(configuration.device_build_path):
	if os.path.isdir(os.path.join(configuration.device_build_path, entry)):
		id = int(entry.split('_')[-1])
		arduino_builds.append([build_data(arduino_boards[id], entry, arduino_board_targets[id].targets), True])

if len(arduino_builds) == 0:
	logger.error('No device builds found')
	sys.exit(1)

upload_targets = MakeTargets.load_all_make_targets(os.path.join(configuration.device_output_path, 'all_upload_targets.txt'))

# Perform uploading and job distribution management
# List of threads that we've executed.
testjobs = []
while len(upload_targets) > 0:
	for arduino_build in arduino_builds:
		if arduino_build[1]:
			found_compatible_device = False

			for upload_target in upload_targets:
				for arduino_target in arduino_build[0].targets:
					if upload_target == arduino_target:
						args = {'target_name': upload_target, 'arduino_build': arduino_build, 'output_dir': configuration.device_output_path}
						thread = threading.Thread(target=upload_and_read_serial, kwargs=args)
						thread.setName(arduino_build[0].arduino.board_type + ', ' + upload_target)
						testjobs.append(thread)
						arduino_build[1] = False
						thread.start()

						upload_targets.remove(upload_target)
						found_compatible_device = True
						break

				if found_compatible_device:
					break

		time.sleep(0.1)

# Wait for all jobs to finish
for job in testjobs:
	job.join()

# Post-process all of the PlanckUnit output files created to convert them to xunit style
planckserial_filename_regex = planck_serial.output_filename_syntax.replace('{target_name}', r'(?P<target_name>.*?)').replace('{suite_no}', r'(?P<suite_no>.*?)')
for test_file in os.listdir(configuration.device_output_path):
	match_obj = re.search(planckserial_filename_regex, test_file)
	if not match_obj:
		logger.error(test_file + ' did not conform to the expected output filename format')
		continue

	test_info = match_obj.groupdict()

	xunit_outputfname = os.path.join(configuration.device_output_path, 'xunit_{target_name}_{suite_no}_output.txt').format(**test_info)

	logger.info('Adapting {pl} -> {xl}...'.format(pl=test_file, xl=xunit_outputfname))
	with open(os.path.join(configuration.device_output_path, test_file), 'r+') as planck_file, open(xunit_outputfname, 'w+') as xunit_file:
		pxa.PlanckAdapter(test_info['target_name'], planck_file, xunit_file).adapt_planck_file()

logger.info('Successfully completed test process.')
