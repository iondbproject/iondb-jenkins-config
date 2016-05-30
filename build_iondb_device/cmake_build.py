import subprocess
import os
import shutil

devnull = open(os.devnull, 'w')


class CMakeBuild:
	@staticmethod
	def do_build(project_dir, build_dir, board_type, port, suppress_output, processor=None, cs_pins=None):
		try:
			shutil.rmtree(project_dir + '/' + build_dir)
		except OSError:
			pass

		os.makedirs(project_dir + '/build')

		command = ['cmake', '-DUSE_ARDUINO=TRUE', '-DBOARD=' + board_type, '-DPORT=' + port]

		if processor is not None:
			command.append('-DPROCESSOR=' + processor)

		if cs_pins is not None:
			list_of_cs_pins = [str(pin) for pin in cs_pins]
			command.append('-DPINS=' + ','.join(list_of_cs_pins))

		command.append("..")

		arguments = {}
		if suppress_output:
			arguments = {'stdout': devnull, 'stderr': devnull}

		return subprocess.call(command, cwd=project_dir + '/build', **arguments)

	@staticmethod
	def do_upload(project_name, project_dir, build_dir, suppress_output):
		arguments = {}
		if suppress_output:
			arguments = {'stdout': devnull, 'stderr': devnull}

		return subprocess.call(['make', project_name + '-upload'], cwd=project_dir + '/build', **arguments)

	@staticmethod
	def clean_build(build_dir):
		try:
			shutil.rmtree(build_dir + '/build')
		except OSError:
			pass