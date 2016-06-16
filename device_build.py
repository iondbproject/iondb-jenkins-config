#!/usr/bin/env python3
import getopt
import logging
import os
import sys
from colorama import Fore, Style

import configuration

sys.path.append('device_helper_files/')
from arduino_boards_serial import ArduinoBoardsSerial, ArduinoBoard
from cmake_build import CMakeBuild
from make_targets import MakeTargets, BoardTargets

logger = logging.getLogger(__name__)
logger.addHandler(configuration.device_logger)
logger.addHandler(configuration.console_logger)


def print_help():
	'''
	Prints help information
	'''
	logger.warning('\nBy leaving the parameters blank, the connected Arduino boards will be detected automatically.')
	logger.warning('Alternatively, you may add a board single OR add a file that includes the definitions for multiple boards.')
	logger.warning('\nUsage:')
	logger.warning('\n  device_build.py [-b board_type [-m processor -p port]] [-f boards_file]\n')

#------------------
# Parse arguments
#------------------

argv = sys.argv[1:]

board_type = None
processor = None
port = None
board_file = None

try:
	opts, args = getopt.getopt(argv, 'b:m:p:f:', ['board=', 'mcu=', 'port=', 'board_file='])
except getopt.GetoptError:
	print_help()
	sys.exit(1)

for opt, arg in opts:
	if opt in ('-b', '--board'):
		board_type = arg
	elif opt in ('-m', '--mcu'):
		processor = arg
	elif opt in ('-p', '--port'):
		port = arg
	elif opt in ('-f', '--board_file'):
		board_file = arg

if board_type is None and (processor is not None or port is not None):
	logger.error('When specifying a processor type or port, you must also specify the board type.\n')
	print_help()
	sys.exit(1)
if board_type is not None and board_file is not None:
	logger.error('You cannot specify both a board and a boards file.')
	print_help()
	sys.exit(1)

# TODO: If a board file is passed in, parse that
board_types = []
processors = []
ports = []

if board_type != None:
	board_types = [board_type]

if processor != None:
	processors = [processor]

if port != None:
	ports = [port]

if len(processors) > 0 and len(processors) != len(board_types):
	logger.error('There are more processors specified than there are boards')
	sys.exit(1)

if len(ports) > 0 and len(ports) != len(board_types):
	logger.error('There are more ports specified than there are boards')
	sys.exit(1)

#--------------------------------------------------------------------------------------------
# Match ports to devices if the ports are not specified and check conditions for each device
#--------------------------------------------------------------------------------------------

arduino_boards = []

if len(ports) == 0:
	logger.info('Finding Arduino boards and their corresponding ports')
	arduino_boards = ArduinoBoardsSerial.get_connected_arduino_boards(board_types, processors, configuration.test_for_conditions)

	if not ArduinoBoardsSerial.save_arduino_boards(arduino_boards, configuration.device_output_path + 'connected_arduino_boards.txt'):
		logger.error("Failed to save Arduino boards to a file")
		sys.exit(1)
else:
	for i in range(len(board_types)):
		if len(processors) > 0:
			processor = processors[i] # TODO: This could be an issue later when using boards file

		arduino_board = ArduinoBoard(board_types[i], i, processor, ports[i])
		if configuration.test_for_conditions:
			if ArduinoBoardsSerial.condition_test(arduino_board, True):
				arduino_boards.append(arduino_board)
		else: # TODO: maybe have option check to see if board works
			arduino_boards.append(arduino_board)

if len(arduino_boards) == 0:
	logger.error('No sufficient Arduino boards found')
	sys.exit(1)

#--------------------
# Build the project
#--------------------

# Generate Makefiles
logger.info('CMake is generating Makefiles for each Arduino board...')

for arduino_board in arduino_boards:
	if CMakeBuild.do_cmake_build(configuration.project_path,
								 os.path.join(configuration.device_build_path, arduino_board.board_type + '_' + str(arduino_board.id)),
								 arduino_board.board_type,
								 arduino_board.port,
								 arduino_board.processor,
								 arduino_board.conditions).status != 0:
		logger.error('  Failed building Makefiles with CMake for ' + arduino_board.board_type)
		sys.exit(1)

	logger.info('  Successfully built Makefiles for ' + arduino_board.board_type)

# Get upload targets from Makefiles
upload_targets = MakeTargets.get_upload_targets(os.path.join(configuration.device_build_path,
												arduino_boards[0].board_type + '_' + str(arduino_boards[0].id)))
upload_targets = dict.fromkeys(upload_targets, 0)
arduino_board_targets = []

logger.info('Building targets for each Arduino board...')

builds_failed = False

# Record which targets will work on which device
for arduino_board in arduino_boards:
	logger.info('Building targets for ' + arduino_board.board_type)
	board_targets = []

	for upload_target in upload_targets.keys():
		build_path = os.path.join(configuration.device_build_path, arduino_board.board_type + '_' + str(arduino_board.id))
		build_result = CMakeBuild.execute_make_target(upload_target.rsplit('-', 1)[0],
													  build_path,
													  False)

		if build_result.status != 0:
			logger.error('  Failed to build target ' + (Fore.RED + upload_target + Style.RESET_ALL))
			builds_failed = True
		else:
			logger.info('  Successfully built target ' + (Fore.GREEN + upload_target + Style.RESET_ALL))

			if MakeTargets.check_target_compatibility(build_result.stdout, arduino_board):
				logger.info('    Target will run on this device')
				board_targets.append(upload_target)
				upload_targets[upload_target] += 1

	arduino_board_targets.append(BoardTargets(arduino_board.id, board_targets))

MakeTargets.save_board_make_targets(arduino_board_targets,
									configuration.device_output_path + 'make_board_targets.txt')

no_compatible_devices = False
if 0 in upload_targets.values():
	no_compatible_devices = True
	upload_targets = {k: v for k, v in upload_targets.items() if v != 0}

MakeTargets.save_all_make_targets(list(upload_targets.keys()),
								  configuration.device_output_path + 'all_upload_targets.txt')

if builds_failed:
	logger.error('There are targets that failed to build.')

if no_compatible_devices:
	logger.error('There are targets that cannot be ran because there is no suitable device connected.')

if builds_failed or no_compatible_devices:
	sys.exit(1)

logger.info('Build process finished')
