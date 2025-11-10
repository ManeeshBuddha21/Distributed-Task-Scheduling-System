add_executable(scheduler
    src/main.cpp
    src/scheduler.cpp
    src/task.cpp
    src/profiler.cpp
    src/load_balancer.cpp
)

target_include_directories(scheduler PRIVATE include)

# On Linux, link with stdc++fs for older libstdc++ if needed
if (CMAKE_CXX_COMPILER_ID STREQUAL "GNU")
    target_link_libraries(scheduler stdc++fs)
endif()
