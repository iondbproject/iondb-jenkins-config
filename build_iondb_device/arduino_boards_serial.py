from cmake_build import CMakeBuild
import boards as board_ids
import serial.tools.list_ports
import usb
import colorama
from colorama import Fore, Back, Style
from collections import namedtuple

excluded_ports = ['bluetooth', 'wireless']
cs_pins_to_check = [4, 10]
sd_card_return_type = namedtuple('sd_card_return_type', ['has_sd', 'has_formatted_sd'])
colorama.init()


class ArduinoBoardsSerial:
	@staticmethod
	def save_arduino_boards(arduino_boards, file_name):
		try:
			file = open(file_name, 'w')

			for arduino_board in arduino_boards:
				file.write(repr(arduino_board))

			file.close()
		except IOError:
			print('Failed to save connected Arduino boards to a file')
			return False

		return True

	@staticmethod
	def load_arduino_boards(file_name):
		try:
			with open(file_name) as file:
				lines = file.readlines()
		except IOError:
			print('Failed to read Arduino boards from file')
			return []

		arduino_boards = []
		for line in lines:
			tokens = [token.strip() for token in line.split(',')]

			if tokens[2] == 'None':
				tokens[2] = None

			if tokens[4] == 'True':
				tokens[4] = True
			else:
				tokens[4] = False

			if tokens[5] == 'True':
				tokens[5] = True
			else:
				tokens[5] = False

			arduino_boards.append(ArduinoBoard(*tokens))

		return arduino_boards

	@staticmethod
	def get_connected_arduino_boards(board_types: 'list of strings' = None, test_for_sd=False) -> 'list of ArduinoBoards':
		if board_types is None or len(board_types) == 0:
			board_types = ArduinoBoardsSerial.get_connected_device_types()

		arduino_boards = [ArduinoBoard(board_type) for board_type in board_types]

		# Get the list of ports for connected devices.
		connected_ports = list(serial.tools.list_ports.comports())
		if len(connected_ports) == 0:
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
			print('Attempting to match ' + (Fore.YELLOW + arduino_board.board_type + Style.RESET_ALL) + ' to a port')
			found_matching_device = False

			# If the type of Arduino is unknown (uses an FTDI) then iterate through all boards with an FTDI.
			if arduino_board.board_type == 'generic':
				test_board_types = [test_board for test_board, id_pair in board_ids.boards.items() if not id_pair]
			else:
				test_board_types = [arduino_board.board_type]

			for test_board_type in test_board_types:
				# Check to see if there is more than one mcu
				test_processors = ['undefined']
				if test_board_type in board_ids.processors:
					test_processors = board_ids.processors[test_board_type]

				for test_processor in test_processors:
					if arduino_board.port is None:
						for connected_port in connected_ports:
							# TODO: Only compile the first time and then use the fast upload
							if ArduinoBoardsSerial.is_correct_device(test_board_type, test_processor, connected_port.device):
								arduino_board.port = connected_port.device
								connected_ports.remove(connected_port)
								found_matching_device = True
								break
					elif test_for_sd:
						if ArduinoBoardsSerial.is_correct_device(test_board_type, test_processor, arduino_board.port):
							found_matching_device = True
					else:
						found_matching_device = True

					if found_matching_device:
						if arduino_board.board_type == 'generic':
							arduino_board.board_type = test_board_type

						if test_processor != 'undefined':
							arduino_board.processor = test_processor

						print('Successfully matched ' + (Fore.GREEN + test_board_type + Style.RESET_ALL) +
							  ' to port ' + arduino_board.port)

						if test_for_sd:
							print('Attempting to detect if there is an SD card')
							sd_card_compatibility = ArduinoBoardsSerial.serial_detect_sd_compatibility(arduino_board.port)
							arduino_board.has_sd_card = sd_card_compatibility.has_sd
							arduino_board.has_formatted_sd_card = sd_card_compatibility.has_formatted_sd

							if arduino_board.has_sd_card and arduino_board.has_formatted_sd_card:
								print('Found a formatted SD card')
							elif arduino_board.has_sd_card:
								print('Found an unformatted SD card')
							else:
								print('Did not detect an SD card')

						break

				if found_matching_device:
					break

			if not found_matching_device:
				print('Failed to match ' + (Fore.RED + arduino_board.board_type + Style.RESET_ALL) + ' to a port')
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
			print('An Arduino board was found but the board type is unknown. An attempt to find the type of board will '
				  'be made but this could take quite awhile. It is recommended that you specify the board instead.')

		return board_types

	@staticmethod
	def is_correct_device(board_type, processor, port):
		if processor == 'undefined' or processor is None:
			print('Trying port ' + port)
			processor = None
		else:
			print('Trying port ' + port + ' for mcu ' + processor)

		compile_result = CMakeBuild.do_cmake_build('../', 'test_sketch/build', board_type, port, True, processor, cs_pins_to_check).status
		upload_result = CMakeBuild.execute_make_target('test_sketch-upload', 'test_sketch/build', False, True).status
		CMakeBuild.clean_build('test_sketch/build')

		return compile_result == 0 and upload_result == 0

	@staticmethod
	def check_if_possible_arduino_port(port):
		possible_arduino_port = True

		for excluded_port in excluded_ports:
			if excluded_port in port.lower():
				possible_arduino_port = False
				break

		return possible_arduino_port

	@staticmethod
	def serial_detect_sd_compatibility(port):
		ser = serial.Serial(port, 9600, timeout=20)

		linein = ser.readline().decode('ascii')
		while linein != '':
			if 'SD_CARD' in linein:
				if 'SD_FORMATTED' in linein:
					return sd_card_return_type(has_sd=True, has_formatted_sd=True)

				return sd_card_return_type(has_sd=True, has_formatted_sd=False)

			if str(cs_pins_to_check[-1]) in linein:
				break

			linein = ser.readline().decode('ascii')

		return sd_card_return_type(has_sd=False, has_formatted_sd=False)


class ArduinoBoard:
	def __init__(self, board_type, id=0, processor=None, port=None, has_sd_card=False, has_formatted_sd_card=False):
		self.board_type = board_type
		self.id = id
		self.processor = processor
		self.port = port
		self.has_sd_card = has_sd_card
		self.has_formatted_sd_card = has_formatted_sd_card

	def __str__(self):
		temp_string = self.board_type
		temp_string += ', ID: ' + str(self.id)

		if self.processor is not None:
			temp_string += ', ' + self.processor

		if self.port is not None:
			temp_string += ', ' + self.port

		if self.has_sd_card:
			temp_string += ', SD card'

		if self.has_formatted_sd_card:
			temp_string += ', formatted SD card'

		return temp_string

	def __repr__(self):
		temp_string = str(self.board_type)
		temp_string += ', ' + str(self.id)
		temp_string += ', ' + str(self.processor)
		temp_string += ', ' + str(self.port)
		temp_string += ', ' + str(self.has_sd_card)
		temp_string += ', ' + str(self.has_formatted_sd_card)

		return temp_string

