project(ECBS)

cmake_minimum_required (VERSION 3.7.1)

set(CMAKE_CXX_STANDARD 11)  # only useful when CMake version >= 3.1
set(CMAKE_CXX_COMPILER "/usr/bin/g++")
set(CMAKE_LINKER  "/usr/bin/ld")
set(CMAKE_VERBOSE_MAKEFILE ON)  # Show all commands and parameters

set(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -g -Wall --std=c++11")
set(CMAKE_CXX_FLAGS_DEBUG "-O0")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG ")

include_directories("inc" "src")
include_directories("/Users/apple/Desktop/hta/Courses/USC/MLandOpt/Project/ECBS-master/resources/sparsehash/include")
file(GLOB SOURCES "*src/*.cpp" "*.cpp")
# file(GLOB SOURCES "*src/cbs.cpp" "src/epea.cpp" "src/epea_node.cpp" "src/ecbs.cpp" "src/basic_solver.cpp" 
# "src/grid2D.cpp" "src/common.cpp" "src/node.cpp" "src/single_agent.cpp" "driver.cpp")

# Find Boost
find_package( Boost 1.49.0 REQUIRED COMPONENTS program_options system filesystem)
include_directories( ${Boost_INCLUDE_DIRS} )


add_executable(ECBS ${SOURCES} )
target_link_libraries(ECBS ${Boost_LIBRARIES})
