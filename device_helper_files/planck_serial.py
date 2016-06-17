import sys
import serial
import shutil
import os
import logging

sys.path.append('../')
import configuration

logger = logging.getLogger(__name__)
logger.addHandler(configuration.device_logger)
logger.addHandler(configuration.console_logger)

# Global variables.
opening_tag = "<suite>"
closing_tag = "</suite>"

error_open_tag = "<planck_serial_error>"
error_close_tag = "</planck_serial_error>"

output_filename_syntax = "planckserial_{target_name}_suite_{suite_no}.txt"


class PlanckAbortError(Exception):
	"""Exception that's thrown when planck serial must abort a suite early."""


def parse_serial(output_folder, port, baud_rate=9600, timeout=10, target_name="Planck Serial"):
	# Initialize serial connection.
	# Timeout should be calibrated to ensure enough time for tests to run,
	#   but still be a reasonable wait time if the device stalls or crashes entirely.
	ser = serial.Serial(port, baud_rate, timeout=timeout)

	# Start reading one suite at a time until it returns false. 
	# False implies we hit a crash condition and cannot continue running, so we abort the test case.
	suite_no = 1
	while output_test(ser, suite_no, output_folder, target_name):
		suite_no += 1
		# (keep reading and writing suites until no more found)

	# We're done, close the serial port and quit
	ser.close()


def output_test(ser, suite_no, output_folder, target_name):
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
	filename = os.path.join(output_folder, output_filename_syntax.format(target_name=target_name, suite_no=suite_no))

	# Ensure that all characters are ASCII in order to avoid garbage data.
	# New lines must be already present, or produced in a timely manner
	# (i.e. within the timeout period specified at connection initialization).
	#
	# For now, this assumes we are using the XML style in which <suite> and </suite> tags
	# only occur at the end of lines.
	linein = ""
	#This try is caught by PlanckAbortError.
	try:
		# This try is caught by UnicdeDecodeError.
		try:
			linein = ser.readline()
			# Consume garbage until we see the first <suite> tag
			while b'<suite>' not in linein and linein != b'':
				logger.warning('Threw away: ')
				logger.warning(linein)
				linein = ser.readline()

			if linein != b'':
				linein = opening_tag + linein.rsplit(b'<suite>', 1)[1].decode('ascii')
			else:
				linein = ''

			while linein != '':

				# If opening tag comes up while already in suite, treat it as
				# a device crash/restart, and reset suite contents accordingly.
				opening_found = linein.find(opening_tag)
				if opening_found != -1:
					if in_suite:
						raise PlanckAbortError(gen_error_tag("Aborted suite " + str(suite_no) + " from reset loop crash."))
					else:
						# (Since it may be on the same line as discarded data,
						#   just include the tag and newline.)
						in_suite = True
						lines.append(linein[:len(opening_tag) + 1])

				# If we find a closing tag and are in a suite (i.e. not catching old data), write the contents.
				elif closing_tag in linein and in_suite:
					lines.append(linein)

					flush_to_file(filename, lines)

					# End suite and return that we were successful.
					in_suite = False
					return True

				# Other types of lines should be ignored if not contained in a suite,
				# otherwise they are test data and should be added as-is.
				elif in_suite:
					lines.append(linein)

				linein = ser.readline()
				linein = linein.decode("ascii")

			# Land here on timeout (from crash, or end of data).
			# If we didn't find a closing tag by the end, we must abort this suite.
			if in_suite:
				raise PlanckAbortError(gen_error_tag("Aborted suite " + str(suite_no) + " from stall or lack of closing tag."))
			else:
				# print("******* UNHANDLED PLANCK_SERIAL EXIT CASE! ********")
				return False

		# Cancel and give an error if a non-ASCII character is ever found in the data.
		except UnicodeDecodeError:
			logger.error("Line: ")
			logger.error(linein)
			raise PlanckAbortError(gen_error_tag("Non-ASCII characters found in output. Please check the source text and baud rate."))

	except PlanckAbortError as pae:
		logger.error(str(pae).replace(error_open_tag, "").replace(error_close_tag, ""))

		lines.append(str(pae) + "\n")
		flush_to_file(filename, lines)

		# Abort the test target since we had a fatal error.
		return False


def gen_error_tag(msg):
	return "{perropen}{errmsg}{perrclose}".format(perropen=error_open_tag, errmsg=msg, perrclose=error_close_tag)


def flush_to_file(filename, lines):
	with open(filename, 'w') as f:
		f.writelines(lines)