import subprocess
from subprocess import Popen, PIPE, STDOUT
import os
import sys
import shutil
from collections import namedtuple

build_result = namedtuple('build_result', ['status', 'output'])
devnull = open(os.devnull, 'w')


class CMakeBuild:
	@staticmethod
	def do_cmake_build(project_path_rel_build_dir, build_dir, board_type, port, suppress_output,
					   processor=None, cs_pins=None):
		try:
			shutil.rmtree(build_dir)
		except OSError:
			pass

		try:
			os.makedirs(build_dir)
		except OSError:
			print('Failed to create build directory')
			sys.exit(1)

		command = ['cmake', '-DUSE_ARDUINO=TRUE', '-DBOARD=' + board_type, '-DPORT=' + port]

		if processor is not None:
			command.append('-DPROCESSOR=' + processor)

		if cs_pins is not None:
			list_of_cs_pins = [str(pin) for pin in cs_pins]
			command.append('-DPINS=' + ','.join(list_of_cs_pins))

		command.append(project_path_rel_build_dir)

		proc = subprocess.Popen(command, cwd=build_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		output = ''
		while proc.poll() is None:
			line = proc.stdout.readline().decode('ascii')

			if not suppress_output:
				print(line, end='')

			output += line

		proc.wait(120)

		return build_result(proc.returncode, output)

	@staticmethod
	def execute_make_target(target_name, build_dir, fast, suppress_output):
		if fast:
			target_name += '/fast'

		proc = subprocess.Popen(['make', target_name], cwd=build_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

		output = ''
		while proc.poll() is None:
			line = proc.stdout.readline().decode('ascii')

			if not suppress_output:
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