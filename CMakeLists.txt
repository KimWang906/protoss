cmake_minimum_required(VERSION 3.1)

project(protobuf-example)

set(Protobuf_PREFIX_PATH
    "/home/xx/soft/protobuf-3.8.0/include"            
    "/home/xx/soft/protobuf-3.8.0/lib"             
    "/usr/local/bin/" )
list(APPEND CMAKE_PREFIX_PATH "${Protobuf_PREFIX_PATH}")

include_directories(include)
set(CMAKE_CXX_STANDARD 17) 
set(CMAKE_CXX_STANDARD_REQUIRED on)
# set(CMAKE_CXX_FLAGS "${CMAKE_CXX_FLAGS} -Wall -Wextra -Werror")

include(FindProtobuf)
find_package(Protobuf REQUIRED)
include_directories(${PROTOBUF_INCLUDE_DIRS})

# to find *.bp.h files
include_directories(${CMAKE_CURRENT_BINARY_DIR})

protobuf_generate_cpp(PROTO_SRC PROTO_HEADER proto/protoss.proto)
add_library(proto ${PROTO_HEADER} ${PROTO_SRC})
add_executable(main main.cpp)
target_link_libraries(main proto ${PROTOBUF_LIBRARY})