import logging
import os
import shutil
import subprocess
import sys
from collections import namedtuple

sys.path.append('../')
import configuration

sys.path.append('helper_files/')
import helper_functions

build_result = namedtuple('build_result', ['status', 'output'])

logger = logging.getLogger(__name__)
logger.addHandler(configuration.device_logger)
logger.addHandler(configuration.console_logger)


class CMakeBuild:
	@staticmethod
	def do_cmake_build(abs_project_path, build_dir, board_type, port, processor=None, target_conditions=None):
		helper_functions.remove_directory(build_dir)

		try:
			os.makedirs(build_dir)
		except OSError:
			logger.exception('Failed to create build directory')
			sys.exit(1)

		command = ['cmake', '-DUSE_ARDUINO=TRUE', '-DBOARD=' + board_type, '-DPORT=' + port, '-DBAUD_RATE=' +
				   str(configuration.baud_rate)]

		if target_conditions is not None:
			for target_condition in target_conditions:
				if target_condition.cs_pin is not None:
					command.append('-D' + target_condition.library + '_CS=' + str(target_condition.cs_pin))

		if processor is not None:
			command.append('-DPROCESSOR=' + processor)

		command.append(abs_project_path)

		proc = subprocess.Popen(command, cwd=build_dir, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
								universal_newlines=True)
		output = helper_functions.process_output_stream(proc)

		return build_result(proc.returncode, output)

	@staticmethod
	def execute_make_target(target_name, build_dir, fast):
		if fast:
			target_name += '/fast'

		proc = subprocess.Popen(['make', target_name], cwd=build_dir, stdout=subprocess.PIPE, 
		                        stderr=subprocess.STDOUT, universal_newlines=True)
		output = helper_functions.process_output_stream(proc)

		return build_result(proc.returncode, output)
