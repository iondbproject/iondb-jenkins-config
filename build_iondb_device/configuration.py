#=================================================
# User configuration for Arduino build system
#=================================================

# This is the path of where the output build will be.
build_path = '../iondb/build/'

# This path is the path of the project relative to where the build path is.
project_path_rel_to_build_path = '../'

# This is the path where the board definitions and corresponding targets will be saved.
board_info_output_path = 'output/'

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

# Pipe build and debug output to a file. There will still be basic information outputted to the console.
output_to_file = True

# If you are outputting build and debug info to a file, this is the name of that file.
output_file_name = 'build_output.txt'

# Output debugging information to the console. This includes some of the output from building the test_sketch.
output_debug = False

# Output build output to the console
output_build = False

# The baud rate used by the serial monitor
baud_rate = 115200

# The timeout when reading lines from the serial output
timeout = 20