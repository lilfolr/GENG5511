cmake_minimum_required(VERSION 3.6)
project(firewall_visualiser)

set(CMAKE_CXX_STANDARD 11)

set(SOURCE_FILES main.c)
add_executable(firewall_visualiser ${SOURCE_FILES})