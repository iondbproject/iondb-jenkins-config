cmake_minimum_required(VERSION 3.5)

message("Linking against Arduino...")
set(CMAKE_TOOLCHAIN_FILE ${CMAKE_SOURCE_DIR}/cmake/ArduinoToolchain.cmake)
set(PROJECT_NAME test_sketch)
project(test_sketch C CXX)

set(${PROJECT_NAME}_BOARD           ${BOARD})
if(PROCESSOR)
    set(${PROJECT_NAME}_PROCESSOR   ${PROCESSOR})
else()
    set(${PROJECT_NAME}_PROCESSOR)
endif()
set(${PROJECT_NAME}_PORT            ${PORT})
set(${PROJECT_NAME}_SKETCH          test_sketch.ino)

set(${PROJECT_NAME}_SRCS            sd2card/Sd2Card.h
                                    sd2card/Sd2Card.cpp
                                    sd2card/Sd2PinMap.h
                                    sd2card/SdInfo.h)

add_definitions("-D BAUD_RATE=${BAUD_RATE}")

generate_arduino_firmware(${PROJECT_NAME})