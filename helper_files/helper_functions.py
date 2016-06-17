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
	for line in iter(process.stdout.readline, ''):
		stdout_line = line.strip()

		logger.debug(stdout_line)
		stdout += stdout_line + '\n'

	if process.poll() is None:
		logger.critical("Exit early")

	return stdout


def create_directory(directory, delete_existing=False):
	if delete_existing:
		remove_directory(directory)

	try:
		os.makedirs(directory)
	except OSError:
		logger.exception('Could not create the directory "' + directory + '"')


def remove_directory(directory):
	try:
		shutil.rmtree(directory)
	except OSError:
		logger.warning('Could not remove ' + directory + '. It may not exist.')
