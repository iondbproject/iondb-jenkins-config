import subprocess
import os
import sys
import shutil
from collections import namedtuple

sys.path.append('../')

import configuration

build_result = namedtuple('build_result', ['status', 'output'])


class CMakeBuild:
	@staticmethod
	def do_cmake_build(project_path_rel_build_dir, build_dir, board_type, port, output_to_console, processor=None, target_conditions=None):
		try:
			shutil.rmtree(build_dir)
		except OSError:
			pass

		try:
			os.makedirs(build_dir)
		except OSError:
			print('Failed to create build directory')
			sys.exit(1)

		command = ['cmake', '-DUSE_ARDUINO=TRUE', '-DBOARD=' + board_type, '-DPORT=' + port, '-DBAUD_RATE=' + str(configuration.baud_rate)]

		if target_conditions is not None:
			for target_condition in target_conditions:
				if target_condition.cs_pin is not None:
					command.append('-D' + target_condition.library + '_CS=' + str(target_condition.cs_pin))

		if processor is not None:
			command.append('-DPROCESSOR=' + processor)

		command.append(project_path_rel_build_dir)

		proc = subprocess.Popen(command, cwd=build_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, universal_newlines=True)

		output = ''
		while proc.poll() is None:
			line = proc.stdout.readline()

			if output_to_console:
				print(line, end='')

			output += line

		proc.wait(120)

		return build_result(proc.returncode, output)

	@staticmethod
	def execute_make_target(target_name, build_dir, fast, output_to_console):
		if fast:
			target_name += '/fast'

		proc = subprocess.Popen(['make', target_name], cwd=build_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT
		                        universal_newlines=True)

		output = ''
		while proc.poll() is None:
			line = proc.stdout.readline()

			if output_to_console:
				print(line, end='')

			output += line

		proc.wait(120)

		return build_result(proc.returncode, output)

	@staticmethod
	def clean_build(build_dir):
		try:
			shutil.rmtree(build_dir)
		except OSError:
			pass