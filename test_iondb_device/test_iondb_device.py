#!/usr/bin/python

import os
import subprocess
import re
import sys
from collections import namedtuple
import planck_serial

sys.path.append('../build_iondb_device/')

from cmake_build import CMakeBuild

dir_port_pair = namedtuple('dir_port_pair', ['directory', 'port'])


def get_upload_targets(dir):
	proc = subprocess.Popen(['make', '-qp'], cwd=dir, stdout=subprocess.PIPE)
	output = proc.stdout.read()

	targets = re.findall(r'^([^# \/\t\.%]*):[^=]?', output.decode('ascii'), flags=re.MULTILINE)
	targets = [target.strip() for target in targets]
	targets.remove('Makefile')
	targets = [target for target in targets if "-upload" in target]

	return targets


dir_port_pairs = []
for entry in os.listdir('build/'):
	if os.path.isdir('build/' + entry):
		port = entry.split('_', 1)[1]
		port = port.replace('.-.', '/')
		dir_port_pairs.append(dir_port_pair(entry, port))

if len(dir_port_pairs) == 0:
	print('No device builds found')
	sys.exit(1)

upload_targets = get_upload_targets('build/' + dir_port_pairs[0].directory)

for upload_target in upload_targets:
	print(upload_target)
	CMakeBuild.do_upload('test_open_address_hash-upload', 'build/' + dir_port_pairs[0].directory, False)
	planck_serial.parse_serial('test_results', dir_port_pairs[0].port, print_info=True, clear_folder=True)