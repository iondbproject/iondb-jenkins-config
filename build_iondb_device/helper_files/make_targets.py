import subprocess
import re
import sys

sys.path.append('../')

import configuration


class MakeTargets:
	@staticmethod
	def get_upload_targets(dir):
		proc = subprocess.Popen(['make', '-qp'], cwd=dir, stdout=subprocess.PIPE, universal_newlines=True)
		output = proc.stdout.read()

		targets = re.findall(r'^([^# \/\t\.%]*):[^=]?', output, flags=re.MULTILINE)
		targets = [target.strip() for target in targets]
		targets.remove('Makefile')
		targets = [target for target in targets if "-upload" in target]

		return targets

	@staticmethod
	def check_target_compatibility(target_output, arduino_board):
		arduino_build_conditions = [condition.library for condition in arduino_board.conditions]
		for build_condition in configuration.conditions:
			if build_condition[1] is not None:
				if build_condition[1] in target_output and build_condition[0] not in arduino_build_conditions:
					return False

		program_size_percentages = re.findall('\[Program: \d+ bytes \((\d+\.\d+)%\)\]', target_output)
		data_size_percentages = re.findall('\[Program: \d+ bytes \((\d+\.\d+)%\)\]', target_output)

		for program_percentage in program_size_percentages:
			if float(program_percentage) > configuration.max_program_size_percentage:
				return False

		for data_percentage in data_size_percentages:
			if float(data_percentage) > configuration.max_dynamic_memory_percentage:
				return False

		return True

	@staticmethod
	def save_all_make_targets(targets, file_name):
		try:
			file = open(file_name, 'w')

			for target in targets:
				file.write(target + '\n')

			file.close()
		except IOError:
			print('Failed to save make targets to a file')
			return False

		return True

	@staticmethod
	def load_all_make_targets(file_name):
		try:
			with open(file_name) as file:
				targets = file.readlines()
		except IOError:
			print('Failed to read make targets from file')
			return []

		return [target.strip() for target in targets]

	@staticmethod
	def save_board_make_targets(board_targets, file_name):
		board_targets.sort(key=lambda x: x.id, reverse=False)

		try:
			file = open(file_name, 'w')

			for board_target in board_targets:
				file.write(repr(board_target) + '\n')

			file.close()
		except IOError:
			print('Failed to save make targets to a file')
			return False

		return True


	@staticmethod
	def load_board_make_targets(file_name):
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
			board_targets.append(BoardTargets(board_id, tokens))

		board_targets.sort(key=lambda x: x.id, reverse=False)

		return board_targets


class BoardTargets:
	def __init__(self, id, targets):
		self.id = id
		self.targets = targets

	def __str__(self):
		temp_string = str(self.id)
		temp_string += ', Targets: ' + str(self.targets)

		return temp_string

	def __repr__(self):
		temp_string = str(self.id)

		for target in self.targets:
			temp_string += ', ' + target

		return temp_string
