#include "profiler.hpp"
#include <iostream>

Profiler::Profiler(const std::string& path)
    : path_(path), stop_(false) {}

// starts a background thread that writes periodic stats
void Profiler::start(std::function<void(std::ofstream&)> dump_fn) {
    stop_.store(false);
    th_ = std::thread([this, dump_fn]() {
        std::ofstream out(path_, std::ios::out | std::ios::trunc);
        if (!out.is_open()) {
            std::cerr << "[profiler] failed to open " << path_ << std::endl;
            return;
        }
        out << "ts_ms,queued,total_done\n";
        while (!stop_.load()) {
            try {
                dump_fn(out);
                out.flush();
            } catch (...) {
                std::cerr << "[profiler] error while dumping stats\n";
            }
            std::this_thread::sleep_for(std::chrono::seconds(1));
        }
        out.close();
        std::cout << "[profiler] stopped\n";
    });
}

void Profiler::stop() {
    stop_.store(true);
    if (th_.joinable()) th_.join();
}
