#pragma once
#include <string>
#include <vector>
#include <filesystem>
#include <atomic>
#include <thread>
#include <mutex>
#include "task_queue.hpp"
#include "load_balancer.hpp"
#include "profiler.hpp"

class Scheduler {
public:
    Scheduler(int workers, const std::string& queue_dir, const std::string& completed_dir);
    ~Scheduler();

    void run();
    void stop();

private:
    void poller_loop_();
    void worker_loop_(int wid);
    bool run_task_(int wid, Task& t);
    static Task parse_task_file_(const std::filesystem::path& p);
    static void write_done_file_(const std::filesystem::path& completed_dir, const Task& t);
    static void requeue_task_file_(const std::filesystem::path& queue_dir, const Task& t);

    int workers_;
    std::filesystem::path qdir_, cdir_;
    TaskQueue q_;
    std::atomic<bool> stop_{false};
    std::vector<std::thread> pool_;
    std::thread poller_;
    Profiler profiler_;
    std::atomic<uint64_t> total_done_{0};
    std::mutex seen_mtx_;
    std::unordered_set<std::string> seen_;
};
