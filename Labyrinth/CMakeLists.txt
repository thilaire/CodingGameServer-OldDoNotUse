cmake_minimum_required(VERSION 3.5)

project(Labyrinth)

set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -g -std=c11 -Wall")
 
include_directories(../GameAPI/)


set(SRC_BABYLABY src/mainbaby.c)
set(SRC_Q1 src/Q1.c)

set(SRC_API API/labyrinthAPI.h API/labyrinthAPI.c)
set(GAME_API ../GameAPI/GameAPI.h ../GameAPI/ret_type.h ../GameAPI/GameAPI.c)

set(EXECUTABLE_OUTPUT_PATH bin/${CMAKE_BUILD_TYPE})

#include_directories(.)
add_executable(babyLaby ${SRC_API} ${SRC_BABYLABY} ${GAME_API})
add_executable(Q1 ${SRC_API} ${SRC_Q1} ${GAME_API})



