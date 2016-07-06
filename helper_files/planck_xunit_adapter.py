#!/usr/bin/env python3
import sys
import re
import string
import logging
import functools
from contextlib import contextmanager

sys.path.append('../')
import configuration

logger = logging.getLogger(__name__)
logger.addHandler(configuration.device_logger)
logger.addHandler(configuration.pc_logger)
logger.addHandler(configuration.console_logger)


# Outputs PlanckUnit test results in JUnit XML spec.
class PlanckAdapter:
	def __init__(self, suite_name, target_file, destination_file=sys.stdout):
		self.suite_name = suite_name
		self.target_file = target_file
		self.destination_file = destination_file
		# This is a wrapper around the print function that redirects output to dest. file.
		self.pxa_print = functools.partial(print, file=self.destination_file)

	def write_xml_header(self):
		self.pxa_print('<?xml version="1.0" encoding="UTF-8"?>')

	@contextmanager
	def write_xunit_tag(self, tag_name, attributes=None):
		if attributes is None:
			attributes = {}

		self.pxa_print('<{tag} '.format(tag=tag_name), end='')
		for key,val in attributes.items():
			self.pxa_print('{key}=\"{val}\" '.format(key=key, val=val), end='')
		self.pxa_print('>')

		yield

		self.pxa_print('</{tag}>'.format(tag=tag_name))

	def adapt_planck_file(self):
		test_case_re = re.compile(r'<test>name:\"(?P<name>.*?)\",line:\"(?P<line>.*?)\",file:\"(?P<file>.*?)\",function:\"(?P<function>.*?)\",time:\"(?P<time>.*?)\",message:\"(?P<message>.*?)\"<\/test>')
		summary_re = re.compile(r'<summary>total_tests:\"(?P<total_tests>.*?)\",total_passed:\"(?P<total_passed>.*?)\"<\/summary>')
		error_re = re.compile(r'<planck_serial_error>(?P<error_msg>.*?)<\/planck_serial_error>')
		testname_re = re.compile(r'<testname>(.*)<\/testname>')
		testcount_re = re.compile(r'<testcount>(.*)<\/testcount>')

		test_cases = {}
		test_names = []
		summary = {}
		error_msg = ''
		expected_test_count = 0
		for line in self.target_file:
			line = ''.join(c for c in line if c in string.printable)

			match_obj = test_case_re.search(line)
			if match_obj:
				case_dict = match_obj.groupdict()
				test_cases[case_dict['name']] = case_dict

			summ_obj = summary_re.search(line)
			if summ_obj:
				if summary:
					for k,v in summ_obj.groupdict().items():
						summary[k] += int(v)
				else:
					summary = {k:int(v) for k,v in summ_obj.groupdict().items()}

			error_obj = error_re.search(line)
			if error_obj:
				error_msg = error_obj.group(1)

			testname_obj = testname_re.search(line)
			if testname_obj:
				test_names.append(testname_obj.group(1))

			testcount_obj = testcount_re.search(line)
			if testcount_obj:
				expected_test_count += int(testcount_obj.group(1))

		summary['total_failed'] = len(test_names) - len(test_cases)
									# int(summary.get('total_tests', 0))
		runattrs = {
			'name': self.suite_name,
			'project': 'IonDB',
			'tests': len(test_names),
			'started': len(test_cases),
			'failures': summary.get('total_failed', 0),
			'errors': 0,
			'ignored': 0,
		}

		self.write_xml_header()
		with self.write_xunit_tag('testrun', runattrs):
			with self.write_xunit_tag('testsuite', {'name': self.suite_name, 'time': sum([float(case['time']) for case in test_cases.values()])}):
				# If PlanckSerial reported an error, then we want to write a special 'testcase' for this error.
				if error_msg:
					error_attrs = {
						'name': '_planck_error',
						'classname': self.suite_name,
						'time': '0.0',
					}

					with self.write_xunit_tag('testcase', error_attrs):
						with self.write_xunit_tag('failure'):
							self.pxa_print(error_msg)

				for case_name in test_names:
					case = test_cases.get(case_name, {})
					case_attrs = {
						'name': '{base_name}'.format(base_name=case_name),
						'classname': self.suite_name,
						'time': case.get('time', '0.0'),
					}

					with self.write_xunit_tag('testcase', case_attrs):
						if not case:
							with self.write_xunit_tag('failure'):
								self.pxa_print('We expected this test to run, but it was not.')
							continue

						if case['line'] != '-1': #if fail
							with self.write_xunit_tag('failure'):
								self.pxa_print(
									'Failed in function "{func}", at {filen}:{line}: {msg}'.format(
										func=case['function'],
										filen=case['file'],
										line=case['line'],
										msg=case['message']
									)
								)                                           

if __name__ == '__main__':
	import fileinput

	with fileinput.input() as fin:
		PlanckAdapter("Terminal test", fin).adapt_planck_file()
