#pragma once
#include <atomic>
#include <thread>
#include <fstream>
#include <chrono>
#include <functional>

class Profiler {
public:
    using Clock = std::chrono::steady_clock;
    Profiler(const std::string& path): path_(path) {}
    void start(std::function<void(std::ofstream&)> dump_fn) {
        stop_.store(false);
        th_ = std::thread([this, dump_fn](){
            std::ofstream out(path_, std::ios::out);
            out << "ts_ms,queued,total_done
";
            while (!stop_.load()) {
                dump_fn(out);
                out.flush();
                std::this_thread::sleep_for(std::chrono::seconds(1));
            }
        });
    }
    void stop() {
        stop_.store(true);
        if (th_.joinable()) th_.join();
    }
private:
    std::string path_;
    std::atomic<bool> stop_{false};
    std::thread th_;
};
