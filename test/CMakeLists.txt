cmake_minimum_required(VERSION 3.9)

set(CMAKE_CXX_COMPILER /usr/bin/g++)

# Specify the project name
project(poc)

# Declare the project target
add_executable(${PROJECT_NAME} poc.cpp)

# Add the directory containing the shared libraries to the linker's search path
target_link_directories(${PROJECT_NAME} PUBLIC "libs")

# Link the shared libraries
target_link_libraries(${PROJECT_NAME}
    -lfmt
    libc.so.6
    libmysqlclient.so.21
    libstdc++.so.6
)
