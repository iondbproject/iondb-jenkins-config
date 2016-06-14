import sys
import os

sys.path.append('../')
import configuration


def process_output_stream(process, output_to_console):
	file = None
	if configuration.output_to_file:
		try:
			file = open(os.path.join(configuration.board_info_output_path, configuration.output_file_name), 'a')
		except OSError as e:
			print('Failed to open build/debug output file.')
			print(e)
			sys.exit(1)

	output = ''
	while process.poll() is None:
		line = process.stdout.readline()

		if output_to_console:
			print(line, end='')

		if configuration.output_to_file:
			try:
				file.write(line)
			except OSError as e:
				print('Failed to write to build/debug output file.')
				print(e)
				sys.exit(1)

		output += line

	if configuration.output_to_file:
		try:
			file.close()
		except OSError as e:
			print('Failed to close build/debug output file.')
			print(e)
			sys.exit(1)

	process.wait(120)

	return output


def output_error_to_file(error):
	if configuration.output_to_file:
		try:
			file = open(configuration.output_file_name, 'a')
			file.write(error)
			file.close()
		except OSError as e:
			print('Failed to write to build/debug output file.')
			print(e)
			sys.exit(1)
