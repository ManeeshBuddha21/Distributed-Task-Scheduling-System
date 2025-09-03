
cmake_minimum_required(VERSION 3.16)
project(worker CXX)
set(CMAKE_CXX_STANDARD 17)
add_executable(worker src/main.cpp)
find_package(CURL REQUIRED)
target_link_libraries(worker CURL::libcurl)
