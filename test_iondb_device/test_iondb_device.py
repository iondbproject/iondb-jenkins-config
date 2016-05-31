#!/usr/bin/python

import os
import subprocess
import re
import sys
import threading
from collections import namedtuple
import planck_serial

sys.path.append('../build_iondb_device/')

from cmake_build import CMakeBuild
from arduino_boards_serial import ArduinoBoardsSerial

arduino_build = namedtuple('arduino_build', ['directory', 'arduino', 'targets' 'is_free'])


def upload_and_read_serial(target_name, arduino_build, output_dir):
	arduino_build.is_free = False
	CMakeBuild.execute_make_target(target_name, 'build/' + arduino_build.directory, True, True)
	planck_serial.parse_serial(output_dir, arduino_build.arduino.port, print_info=True, clear_folder=True)
	arduino_build.is_free = True


# Note: We assume that the list of ArduinoBoards is already sorted by ID.
arduino_boards = ArduinoBoardsSerial.load_arduino_boards('connected_arduino_boards.txt')
arduino_builds = []

# Match the Arduino boards to their corresponding builds and targets
for entry in os.listdir('build/'):
	if os.path.isdir('build/' + entry):
		id = int(entry.split('_')[-1])
		arduino_builds.append(arduino_build(arduino_boards[id], entry, True))

if len(arduino_builds) == 0:
	print('No device builds found')
	sys.exit(1)

# Get the list of targets


# Determine targets that require a formatted SD card and lots of memory
for upload_target in upload_targets:
	# TODO: Build each target and check if the SD lib was included and if the memory size is appropriate
	do_test_build(upload_target)

# Perform uploading and job distribution management
for upload_target in upload_targets:
	args = {'target_name': upload_target, 'arduino_build': arduino_builda, 'output_dir': 'test_results'}
	threading.Thread(target=upload_and_read_serial, kwargs=args)
