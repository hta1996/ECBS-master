project(ECBS)

cmake_minimum_required (VERSION 2.8.12)

set(CMAKE_CXX_STANDARD 11)
set(CMAKE_CXX_COMPILER "/auto/usc/gnu/gcc/5.3.0/bin/gcc")
set(CMAKE_C_COMPILER "/auto/usc/gnu/gcc/5.3.0/bin/gcc")

set(CMAKE_CXX_FLAGS  "${CMAKE_CXX_FLAGS} -g -Wall --std=c++11")
set(CMAKE_CXX_FLAGS_DEBUG "-O0")
set(CMAKE_CXX_FLAGS_RELEASE "-O3 -DNDEBUG")

include_directories("inc" "src" "/home/rcf-proj3/sc3/sparsehash/include")
file(GLOB SOURCES "*src/*.cpp" "*.cpp")

add_definitions(-D_GLIBCXX_USE_CXX11_ABI=0)

# Find Boost
find_package(Boost 1.49.0 REQUIRED COMPONENTS program_options system filesystem)
include_directories(${Boost_INCLUDE_DIRS})

add_executable(ECBS ${SOURCES})
target_link_libraries(ECBS ${Boost_LIBRARIES} -lstdc++ -lm)
