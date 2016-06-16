#!/usr/bin/env python3
import logging
import os
import sys
import colorama
import serial.tools.list_ports
import usb
from colorama import Fore, Style
from collections import namedtuple

import board_definitions as board_ids
from cmake_build import CMakeBuild

sys.path.append('../')
import configuration

target_condition = namedtuple("target_condition", ["library", "cs_pin"])
colorama.init()

logger = logging.getLogger(__name__)
logger.addHandler(configuration.device_logger)
logger.addHandler(configuration.console_logger)


class ArduinoBoardsSerial:
	@staticmethod
	def save_arduino_boards(arduino_boards, file_name):
		arduino_boards.sort(key=lambda x: x.id, reverse=False)

		try:
			file = open(file_name, 'w')

			for arduino_board in arduino_boards:
				file.write(repr(arduino_board) + '\n')

			file.close()
		except IOError:
			logger.exception('Failed to save arduino boards to "' + file_name + '"')
			return False

		return True

	@staticmethod
	def load_arduino_boards(file_name):
		try:
			with open(file_name) as file:
				lines = file.readlines()
		except IOError:
			logger.exception('Failed to read Arduino boards from file')
			return []

		arduino_boards = []
		for line in lines:
			tokens = [token.strip() for token in line.split(',')]

			if tokens[2] == 'None':
				tokens[2] = None

			conditions = []
			for i in range(4, len(tokens), 2):
				if tokens[i + 1] == 'None':
					tokens[i + 1] = None
				conditions.append(target_condition(tokens[i], tokens[i + 1]))

			arduino_boards.append(ArduinoBoard(tokens[0], int(tokens[1]), tokens[2], tokens[3], conditions))

		arduino_boards.sort(key=lambda x: x.id, reverse=False)

		return arduino_boards

	@staticmethod
	def get_connected_arduino_boards(board_types=None, processors=None, test_for_conditions=False):
		if board_types is None or len(board_types) == 0:
			board_types = ArduinoBoardsSerial.get_connected_device_types()

		arduino_boards = []
		for i in range(len(board_types)):
			processor = None
			if processors is not None and len(processors) > 0:
				processor = processors[i]

			arduino_boards.append(ArduinoBoard(board_types[i], processor=processor))

		if len(arduino_boards) == 0:
			return []

		temp_string = ''
		for arduino_board in arduino_boards:
			temp_string += arduino_board.board_type + ', '

		temp_string = temp_string.rstrip(', ')
		logger.info('  Boards: ' + temp_string)

		# Get the list of ports for connected devices.
		connected_ports = list(serial.tools.list_ports.comports())
		if len(connected_ports) == 0:
			logger.warning('No ports found')
			return []

		# Remove ports that contain specific names. For example, bluetooth and wireless
		connected_ports = [port for port in connected_ports if
						   ArduinoBoardsSerial.check_if_possible_arduino_port(port.device)]

		# Some systems have the ids associated with the serial ports so use those if possible. Boards which use an
		# FTDI won't be matched
		for arduino_board in arduino_boards:
			if arduino_board.port is None and arduino_board.board_type in board_ids.boards:
				for connected_port in connected_ports:
					if connected_port.vid is not None and connected_port.pid is not None:
						for id_pair in board_ids.boards[arduino_board.board_type]:
							if id_pair.vid == connected_port.vid and id_pair.pid == connected_port.pid:
								arduino_board.port = connected_port.device
								connected_ports.remove(connected_port)
								break

						if arduino_board.port is not None:
							break

		num_connected_boards = 0
		connected_arduino_boards = []
		for arduino_board in arduino_boards:
			logger.info('Attempting to match ' + (Fore.YELLOW + arduino_board.board_type + Style.RESET_ALL) + ' to a port')
			found_matching_device = False

			# If the type of Arduino is unknown (uses an FTDI) then iterate through all boards with an FTDI.
			if arduino_board.board_type == 'generic':
				test_board_types = [test_board for test_board, id_pair in board_ids.boards.items() if not id_pair]
			else:
				test_board_types = [arduino_board.board_type]

			for test_board_type in test_board_types:
				test_processors = ['undefined']

				# If processor is defined by user, check to see if there is more than one processor
				if arduino_board.processor is not None:
					test_processors = [arduino_board.processor]
				elif test_board_type in board_ids.processors:
					test_processors = board_ids.processors[test_board_type]

				for test_processor in test_processors:
					if arduino_board.port is None:
						build_before_upload = True

						for connected_port in connected_ports:
							if ArduinoBoardsSerial.is_correct_device(test_board_type, test_processor, connected_port.device, build_before_upload):
								arduino_board.port = connected_port.device
								connected_ports.remove(connected_port)
								found_matching_device = True
								break

							build_before_upload = False
					elif test_for_conditions:
						if ArduinoBoardsSerial.is_correct_device(test_board_type, test_processor, arduino_board.port):
							found_matching_device = True
					else:
						found_matching_device = True

					if found_matching_device:
						if arduino_board.board_type == 'generic':
							arduino_board.board_type = test_board_type

						if test_processor != 'undefined':
							arduino_board.processor = test_processor

						logger.info('  Successfully matched ' + (Fore.GREEN + test_board_type + Style.RESET_ALL) +
							  ' to port ' + arduino_board.port)

						if test_for_conditions:
							ArduinoBoardsSerial.condition_test(arduino_board, False)

						break
				if found_matching_device:
					break

			if not found_matching_device:
				logger.warning('  Failed to match ' + (Fore.RED + arduino_board.board_type + Style.RESET_ALL) + ' to a port')
			else:
				arduino_board.id = num_connected_boards
				connected_arduino_boards.append(arduino_board)
				num_connected_boards += 1

		return connected_arduino_boards

	@staticmethod
	def get_connected_device_types():
		board_types = []
		generic_count = 0

		busses = usb.busses()
		for bus in busses:
			devices = bus.devices

			for device in devices:
				found_same_pid = False

				for board_type, id_pairs in board_ids.boards.items():
					for id_pair in id_pairs:
						if device.idVendor == id_pair.vid:
							if device.idProduct == id_pair.pid:
								board_types.append(board_type)
								found_same_pid = True
								break

					if found_same_pid:
						break

				if not found_same_pid:
					if device.idVendor == board_ids.ftdi:
						generic_count += 1
						break

		# Put generic devices at the end so that the number of checks needed to find actual device is much less
		for i in range(generic_count):
			board_types.append('generic')

		if generic_count > 0:
			logger.warning('An Arduino board was found but the board type is unknown. An attempt to find the type of board will '
				  'be made but this could take quite awhile. It is recommended that you specify the board instead.')

		return board_types

	@staticmethod
	def is_correct_device(board_type, processor, port, build_before=True):
		if processor == 'undefined' or processor is None:
			logger.info('  Trying port ' + port)
			processor = None
		else:
			logger.info('  Trying port ' + port + ' with ' + processor + ' processor')

		compile_result = 0
		if build_before:
			compile_result = CMakeBuild.do_cmake_build('../', 'helper_files/test_sketch/build', board_type, port, processor).status

		fast = False
		if not build_before:
			fast = True

		upload_result = CMakeBuild.execute_make_target('test_sketch-upload', 'helper_files/test_sketch/build', fast).status
		CMakeBuild.clean_build('helper_files/test_sketch/build')

		return compile_result == 0 and upload_result == 0

	@staticmethod
	def condition_test(arduino_board, upload_before=True):
		logger.info('  Attempting condition detection...')

		if upload_before:
			if not ArduinoBoardsSerial.is_correct_device(arduino_board.board_type, arduino_board.processor, arduino_board.port):
				logger.error('Failed to upload to device')
				return False

		conditions = []
		ser = serial.Serial(arduino_board.port, configuration.baud_rate, timeout=configuration.baud_rate)

		linein = ser.readline()
		while b'DONE' not in linein:
			cs_pin = None
			if b'CS_PIN' in linein:
				cs_pin = int(linein.split(b'CS_PIN: ')[1])
				linein = ser.readline()

			for condition in configuration.conditions:
				if str.encode(condition[0]) in linein:
					conditions.append(target_condition(condition[0], cs_pin))
					logger.info('  Condition ' + condition[0] + (Fore.GREEN + ' satisfied' + Style.RESET_ALL))

			linein = ser.readline()

		arduino_board.conditions = conditions
		return True

	@staticmethod
	def check_if_possible_arduino_port(port):
		possible_arduino_port = True

		for excluded_port in configuration.excluded_ports:
			if excluded_port in port.lower():
				possible_arduino_port = False
				break

		return possible_arduino_port


class ArduinoBoard:
	def __init__(self, board_type, id=0, processor=None, port=None, conditions=None):
		self.board_type = board_type
		self.id = id
		self.processor = processor
		self.port = port
		self.conditions = conditions

	def __str__(self):
		temp_string = str(self.board_type)
		temp_string += ', ID: ' + str(self.id)

		if self.processor is not None:
			temp_string += ', ' + str(self.processor)

		if self.port is not None:
			temp_string += ', ' + str(self.port)

		if self.conditions is not None:
			for condition in self.conditions:
				temp_string += ', ' + str(condition.library) + ', ' + str(condition.cs_pin)

		return temp_string

	def __repr__(self):
		temp_string = str(self.board_type)
		temp_string += ', ' + str(self.id)
		temp_string += ', ' + str(self.processor)
		temp_string += ', ' + str(self.port)

		if self.conditions is not None:
			for condition in self.conditions:
				temp_string += ', ' + str(condition.library) + ', ' + str(condition.cs_pin)

		return temp_string

