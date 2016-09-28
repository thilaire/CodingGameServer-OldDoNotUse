cmake_minimum_required(VERSION 3.5)

project(Labyrinth)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -std=c11 -Wall")

set(SRC_BABYLABY babyLaby/mainbaby.c)
set(SRC_Q1 babyLaby/Q1.c)

set(SRC_API clientAPI/labyrinthAPI.h clientAPI/labyrinthAPI.c)

#include_directories(.)
add_executable(babyLaby ${SRC_API} ${SRC_BABYLABY})
add_executable(Q1 ${SRC_API} ${SRC_Q1})



