cmake_minimum_required(VERSION 3.8)

project(protobuf-example)

set(CMAKE_CXX_STANDARD 17) 
set(CMAKE_CXX_STANDARD_REQUIRED on)

include(FindProtobuf)
find_package(Protobuf CONFIG REQUIRED)
include_directories(${PROTOBUF_INCLUDE_DIRS})

# to find *.bp.h files
include_directories(${CMAKE_CURRENT_BINARY_DIR})
protobuf_generate_cpp(PROTO_SRC PROTO_HEADER proto/protoss.proto)
add_library(proto ${PROTO_HEADER} ${PROTO_SRC})

# Set the output directories
set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/build")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/build")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/build")

add_executable(main main.cpp)
target_link_libraries(
  main 
  ${LDFLAGS}
  absl_log_internal_check_op
  absl_log_internal_message
  absl_raw_logging_internal
  absl_spinlock_wait
  proto
  ${PROTOBUF_LIBRARY} 
  )
