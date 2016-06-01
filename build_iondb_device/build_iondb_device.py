#!/usr/bin/python

from arduino_boards_serial import ArduinoBoardsSerial, ArduinoBoard
from cmake_build import CMakeBuild
from make_targets import MakeTargets, BoardTargets
import sys
import getopt
import subprocess
import re


def print_help():
	'''
	Prints help information
	'''
	print('build_iondb_device.py [-b board_type] ...')


def check_target_compatability(target_output, arduino_board):
	if not arduino_board.has_formatted_sd_card:
		if arduino_board.board_type + '_SD' in target_output:
			return False

	program_percentages = re.findall('\[Program: \d+ bytes \((\d+\.\d+)%\)\]', target_output)
	data_percentages = re.findall('\[Program: \d+ bytes \((\d+\.\d+)%\)\]', target_output)

	for program_percentage in program_percentages:
		if float(program_percentage) > 99:
			return False

	for data_percentage in data_percentages:
		if float(data_percentage) > 80:
			return False

	return True

#------------------
# Parse arguments
#------------------

argv = sys.argv[1:]

board_types = []
try:
	opts, args = getopt.getopt(argv,"b:",["board="])
except getopt.GetoptError:
	print_help()
	sys.exit(1)

for opt, arg in opts:
	if opt in ("-b", "--board"):
		board_types.append(arg)

#-------------------------------------
# Clone IonDB and get jenkins-cli.jar
#-------------------------------------

subprocess.call(['git', 'clone', 'https://github.com/iondbproject/iondb.git', 'iondb', '--recursive'], cwd='../')
subprocess.call(['git', 'checkout', 'development'], cwd='../iondb')
subprocess.call(['git', 'submodule', 'init'], cwd='../iondb')
subprocess.call(['git', 'submodule', 'update', '--remote'], cwd='../iondb')

# subprocess.call(['wget', '${JENKINS_URL}jnlpJars/jenkins-cli.jar'], cwd='../')

#--------------------------------------------------------
# Match ports to devices if the ports are not specified
#--------------------------------------------------------

print('Finding Arduino boards')
arduino_boards = ArduinoBoardsSerial.get_connected_arduino_boards(board_types, test_for_sd=True)

if len(arduino_boards) == 0:
	print("No Arduino boards found")
	sys.exit(1)

if not ArduinoBoardsSerial.save_arduino_boards(arduino_boards, 'connected_arduino_boards.txt'):
	print("Failed to save Arduino boards to a file")
	sys.exit(1)

#--------------------
# Build the project
#--------------------

# Generate Makefiles
for arduino_board in arduino_boards:
	if CMakeBuild.do_cmake_build('../../', '../iondb/build/' + arduino_board.board_type + '_' + str(arduino_board.id),
								 arduino_board.board_type, arduino_board.port, False, arduino_board.processor).status != 0:
		print('Failed building Makefiles with CMake')
		sys.exit(1)

# Get upload targets from Makefiles
upload_targets = MakeTargets.get_upload_targets('../iondb/build/' + arduino_boards[0].board_type + '_' + str(arduino_boards[0].id))
arduino_board_targets = []

# Record the targets that which will work on each device
for arduino_board in arduino_boards:
	board_targets = []

	for upload_target in upload_targets:
		build_dir = '../iondb/build/' + arduino_board.board_type + '_' + str(arduino_board.id)
		build_result = CMakeBuild.execute_make_target(upload_target.rsplit('-', 1)[0], build_dir, False, False)

		if build_result.status != 0:
			pass
			# subprocess.call(['java', '-jar', 'jenkins-cli.jar', 'set-build-result unstable'], cwd='../')
		else:
			if check_target_compatability(build_result.output, arduino_board):
				board_targets.append(upload_target)

	arduino_board_targets.append(BoardTargets(arduino_board.id, board_targets))

MakeTargets.save_board_make_targets(arduino_board_targets, 'make_board_targets.txt')
MakeTargets.save_all_make_targets(upload_targets, 'all_upload_targets.txt')
