import sys
import os
import logging

#=============================
# General user configuration
#=============================

# This path is the ABSOLUTE path of the project.
project_path = os.path.abspath('iondb/')

# Build and log output folders. This is the path where the board definitions and corresponding targets will be saved as
# well as the logs and builds.
pc_output_path = os.path.abspath('pc_output/')
pc_build_path = os.path.join(pc_output_path, 'build')
device_output_path = os.path.abspath('device_output/')
device_build_path = os.path.join(device_output_path, 'build')

# Log names
pc_log_name = 'pc_logger.log'
device_log_name = 'device_logger.log'

# Setup loggers
logging.getLogger().setLevel(logging.DEBUG)
console_logger = logging.StreamHandler(sys.stdout)
console_logger.setLevel(logging.INFO)
pc_logger = logging.FileHandler(os.path.join(pc_output_path, pc_log_name))
pc_logger.setLevel(logging.DEBUG)
device_logger = logging.FileHandler(os.path.join(device_output_path, device_log_name))
device_logger.setLevel(logging.DEBUG)

#==============================================
# User configuration for Arduino build system
#==============================================

# If you have ports that you wish to exclude from scanning to speed up the board and port matching process, put the
# name of the port or a substring of the port name here. It is case insensitive.
excluded_ports = ['bluetooth', 'wireless']

# Set this to True if you wish to specify build conditions that will be checked to exclude targets that will not
# run on the device if the conditions are not met. For example, you may wish to see if there is an SD card in the
# device and if it is formatted. You will add the appropriate keywords to test_sketch.ino and then add them here
# as well. You then specify a substring that will be checked for in the build output to see if the target requires
# an SD card or not. The library <card>_SD.a is created on build so '_SD' will suffice to check if the target requires
# an SD card. The conditions array is made up of arrays of 2 entries and the first string is the keyword and the second
# string is the substring to be checked against the build output. You can also specify None if you wish not to check
# a substring against the build output.
test_for_conditions = True
conditions = [['FORMATTED_SD_CARD', '_SD']]

# This is the maximum allowed memory utilization for the code size on device
max_program_size_percentage = 99

# This is the maximum allowed memory utilization for the dynamic memory on device. This does not consider stack
# allocations and memory allocations during runtime so it is advised to not make this 100%.
max_dynamic_memory_percentage = 80

# The baud rate used by the serial monitor
baud_rate = 115200

# The timeout when reading lines from the serial output
timeout = 20
