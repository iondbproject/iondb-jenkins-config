#!/usr/bin/python

import os
import subprocess
import re
import sys
import threading
from collections import namedtuple
import planck_serial

sys.path.append('../build_iondb_device/')

import configuration

sys.path.append('../build_iondb_device/helper_files/')

from cmake_build import CMakeBuild
from arduino_boards_serial import ArduinoBoardsSerial
from make_targets import MakeTargets, BoardTargets

build_data = namedtuple('build_data', ['arduino', 'dir', 'targets'])


def upload_and_read_serial(target_name, arduino_build, output_dir):
	print('test')
	CMakeBuild.execute_make_target(target_name, configuration.build_path + arduino_build[0].dir, False, configuration.output_build)
	planck_serial.parse_serial(output_dir, arduino_build[0].arduino.port, print_info=True, clear_folder=True, baud_rate=configuration.baud_rate)
	arduino_build[1] = True


# Note: The list of ArduinoBoards are already sorted by ID.
arduino_boards = ArduinoBoardsSerial.load_arduino_boards('../build_iondb_device/' + configuration.board_info_output_path + 'connected_arduino_boards.txt')
arduino_board_targets = MakeTargets.load_board_make_targets('../build_iondb_device/' + configuration.board_info_output_path + 'make_board_targets.txt')
arduino_builds = []

# Match the Arduino boards to their corresponding builds and targets
for entry in os.listdir(configuration.build_path):
	if os.path.isdir(configuration.build_path + entry):
		id = int(entry.split('_')[-1])
		arduino_builds.append([build_data(arduino_boards[id], entry, arduino_board_targets[id].targets), True])

if len(arduino_builds) == 0:
	print('No device builds found')
	sys.exit(1)

upload_targets = MakeTargets.load_all_make_targets('../build_iondb_device/' + configuration.board_info_output_path + 'all_upload_targets.txt')

# Perform uploading and job distribution management
while len(upload_targets) > 0:
	for arduino_build in arduino_builds:
		if arduino_build[1]:
			found_compatible_device = False

			for upload_target in upload_targets:
				for arduino_target in arduino_build[0].targets:
					if upload_target == arduino_target:
						args = {'target_name': upload_target, 'arduino_build': arduino_build, 'output_dir': 'test_results'}
						thread = threading.Thread(target=upload_and_read_serial, kwargs=args)
						arduino_build[1] = False
						thread.start()

						upload_targets.remove(upload_target)
						found_compatible_device = True
						break

				if found_compatible_device:
					break
