#!/usr/bin/python

from arduino_boards_serial import ArduinoBoardsSerial
from cmake_build import CMakeBuild
import sys
import getopt
from collections import namedtuple
import re

connected_boards = namedtuple('connected_boards', ['board_list', 'board_ports', 'board_processors'])


def print_help():
	'''
	Prints help information
	'''
	print('build.py [-b board_type] ...')

#------------------
# Parse arguments
#------------------

argv = sys.argv[1:]

board_types = []
try:
	opts, args = getopt.getopt(argv,"b:",["board="])
except getopt.GetoptError:
	print_help()
	sys.exit(2)

for opt, arg in opts:
	if opt in ("-b", "--board"):
		board_types.append(arg)

#--------------------------------------------------------
# Match ports to devices if the ports are not specified
#--------------------------------------------------------

print('Finding Arduino boards')
arduino_boards = ArduinoBoardsSerial.get_connected_arduino_boards(board_types, test_for_sd=True)

if len(arduino_boards) == 0:
	print("No Arduino boards found")
	sys.exit(2)

if not ArduinoBoardsSerial.save_arduino_boards(arduino_boards, 'connected_arduino_boards.txt'):
	print("Failed to save Arduino boards to a file")
	sys.exit(2)

#--------------------
# Build the project
#--------------------

for arduino_board in arduino_boards:
	if CMakeBuild.do_build('../', arduino_board.board_type, arduino_board.port, False, arduino_board.processor) != 0:
		print('Failed to build')


