from arduino_boards_serial import ArduinoBoardsSerial, ArduinoBoard
import subprocess
import re


class MakeTargets:
	@staticmethod
	def get_upload_targets(dir):
		proc = subprocess.Popen(['make', '-qp'], cwd=dir, stdout=subprocess.PIPE)
		output = proc.stdout.read().decode('ascii')

		targets = re.findall(r'^([^# \/\t\.%]*):[^=]?', output, flags=re.MULTILINE)
		targets = [target.strip() for target in targets]
		targets.remove('Makefile')
		targets = [target for target in targets if "-upload" in target]

		return targets

	@staticmethod
	def save_make_targets(board_targets, file_name):
		try:
			file = open(file_name, 'w')

			for board_target in board_targets:
				file.write(repr(board_target))

			file.close()
		except IOError:
			print('Failed to save make targets to a file')
			return False

		return True


	@staticmethod
	def load_make_targets(file_name):
		board_targets = []

		try:
			with open(file_name) as file:
				lines = file.readlines()
		except IOError:
			print('Failed to read make targets from file')
			return []

		for line in lines:
			tokens = [token.strip() for token in line.split(',')]
			board_id = tokens[0]
			tokens.pop(0)
			board_targets.append(BoardTargets(tokens[0], tokens))

		return board_targets


class BoardTargets:
	def __init__(self, board_id, targets):
		self.board_id = board_id
		self.targets = targets

	def __str__(self):
		temp_string = str(self.board_id)
		temp_string += ', Targets: ' + str(self.targets)

		return temp_string

	def __repr__(self):
		temp_string = str(self.board_id)

		for target in self.targets:
			temp_string += ', ' + target

		return temp_string.rsplit(', ', 1)[0]
