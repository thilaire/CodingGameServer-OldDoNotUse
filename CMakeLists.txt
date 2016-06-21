cmake_minimum_required(VERSION 3.5)

project(Labyrinth)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c11 -Wall")

set(SOURCE_FILES
    babyLaby/mainbaby.c
    clientAPI/labyrinthAPI.h
    clientAPI/labyrinthAPI.c)

set(TEST_FILES test/test.c)

#include_directories(.)

add_executable(babyLaby ${SOURCE_FILES})
add_executable(Test ${TEST_FILES} )


