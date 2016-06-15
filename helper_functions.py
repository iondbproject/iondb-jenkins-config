import sys
import os
import shutil
import logging

import configuration

logger = logging.getLogger(__name__)
logger.addHandler(configuration.device_logger)
logger.addHandler(configuration.pc_logger)
logger.addHandler(configuration.console_logger)


def process_output_stream(process):
	output = ''
	while process.poll() is None:
		line = process.stdout.readline()
		logger.debug(line)
		output += line

	process.wait(120)
	return output


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
		logger.exception('"' + directory + '" could not be removed. It may not exit.')