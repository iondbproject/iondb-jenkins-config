import serial
import shutil
import os

# Global variables.
opening_tag = "<suite>"
closing_tag = "</suite>"


def parse_serial(output_folder, port, baud_rate=9600, timeout=120, print_info=False, clear_folder=False):
	# Set up folder structure, if required.
	if clear_folder:
		try:
			shutil.rmtree(output_folder)
		except FileNotFoundError:
			print(output_folder, "No prior output folder found.")
	try:
		os.mkdir(output_folder)
	except FileExistsError:
		pass
	os.chdir(output_folder)

	# Initialize serial connection.
	# Timeout should be calibrated to ensure enough time for tests to run,
	#   but still be a reasonable wait time if the device stalls or crashes entirely.
	ser = serial.Serial(port, baud_rate, timeout=timeout)

	# Start reading one suite at a time until it returns false.
	suite_no = 1
	while output_test(ser, suite_no, print_info):
		suite_no += 1
		# (keep reading and writing suites until no more found)


def output_test(ser, suite_no, print_info):
	"""
	Assuming the project has already been built and uploaded,
	reads serial connection's output for a particular suite and writes it to file.

	Parameters:
	 ser: serial port to listen to
	 suite_no: what count of suite this is at (used in filename)
	 print_info: whether to print lines to console as they are read
	Returns true if a suite was written successfully; otherwise, false.
	"""

	in_suite = False
	lines = []

	# Ensure that all characters are ASCII in order to avoid garbage data.
	# New lines must be already present, or produced in a timely manner
	# (i.e. within the timeout period specified at connection initialization).
	#
	# For now, this assumes we are using the XML style in which <suite> and </suite> tags
	# only occur at the end of lines.
	linein = ""
	try:
		linein = ser.readline().decode("ascii")
		if print_info:
			print("\t" + linein, end="")

		while linein != "":

			# If opening tag comes up while already in suite, treat it as
			# a device crash/restart, and reset suite contents accordingly.
			opening_found = linein.find(opening_tag)
			if opening_found != -1:
				if in_suite:
					lines = []
				else:
					# (Since it may be on the same line as discarded data,
					#   just include the tag and newline.)
					in_suite = True
					lines.append(linein[:len(opening_tag)+1])

			# If we find a closing tag and are in a suite (i.e. not catching old data), write the contents.
			elif closing_tag in linein and in_suite:
				lines.append(linein)
				filename = 'planck_output_' + str(suite_no) + '.txt'

				try:
					with open(filename, 'w') as f:
						for line in lines:
							f.write(line)
				except IOError:
					print("ERROR: Could not write to file " + filename)
					return False
				# End suite and return that we were successful.
				in_suite = False
				return True

			# Other types of lines should be ignored if not contained in a suite,
			# otherwise they are test data and should be added as-is.
			elif in_suite:
				lines.append(linein)

			linein = ser.readline().decode("ascii")
			if print_info:
				print("\t" + linein, end="")

		# Land here on timeout (from crash, or end of data).
		# If we didn't find a closing tag by the end, we must abort this suite.
		if in_suite:
			print("ERROR: Aborted suite "+str(suite_no)+" from stall or lack of closing tag.")
		return False

	# Cancel and give an error if a non-ASCII character is ever found in the data.
	except UnicodeDecodeError:
		print("ERROR: Non-ASCII characters found in output. Please check the source text and baud rate.")
		return False