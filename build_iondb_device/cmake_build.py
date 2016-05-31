import subprocess
import os
import sys
import shutil

devnull = open(os.devnull, 'w')


class CMakeBuild:
	@staticmethod
	def do_build(project_path_rel_build_dir, build_dir, board_type, port, suppress_output, processor=None, cs_pins=None):
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

		arguments = {}
		if suppress_output:
			arguments = {'stdout': devnull, 'stderr': devnull}

		return subprocess.call(command, cwd=build_dir, **arguments)

	@staticmethod
	def do_upload(target_name, build_dir, suppress_output):
		arguments = {}
		if suppress_output:
			arguments = {'stdout': devnull, 'stderr': devnull}

		return subprocess.call(['make', target_name], cwd=build_dir, **arguments)

	@staticmethod
	def clean_build(build_dir):
		try:
			shutil.rmtree(build_dir)
		except OSError:
			pass