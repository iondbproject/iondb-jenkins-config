import sys
import os
import shutil
import logging

sys.path.append('../')
import configuration

logger = logging.getLogger(__name__)
logger.addHandler(configuration.device_logger)
logger.addHandler(configuration.pc_logger)
logger.addHandler(configuration.console_logger)


def process_output_stream(process):
	stdout = ''
	stderr = ''
	while process.poll() is None:
		if process.stdout is not None:
			stdout_line = process.stdout.readline()
			logger.debug(stdout_line.strip())
			stdout += stdout_line

		if process.stderr is not None:
			stderr_line = process.stderr.readline()
			logger.debug(stderr_line.strip())
			stderr += stderr_line

	process.wait(120)
	return stdout, stderr


def create_directory(directory, delete_existing=False):
	if delete_existing:
		remove_directory(directory)

	try:
		os.makedirs(directory)
	except OSError:
		logging.exception('Could not create the directory "' + directory + '"')


def remove_directory(directory):
	try:
		shutil.rmtree(directory)
	except OSError:
		logger.warning('"' + directory + '" could not be removed. It may not exit.')