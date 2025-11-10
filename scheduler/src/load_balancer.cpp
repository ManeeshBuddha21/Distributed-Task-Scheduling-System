#include "load_balancer.hpp"
#include <iostream>
#include <mutex>
#include <thread>
#include <chrono>
#include <random>

static std::mutex log_mtx; // shared console log guard

LoadBalancer::LoadBalancer(int workers)
    : workers_(workers), counter_(0) {
    if (workers_ <= 0) workers_ = 1;
}

int LoadBalancer::pick_worker() {
    // round-robin with a tiny random jitter
    int idx = counter_.fetch_add(1) % workers_;
    if (idx < 0) idx = 0;

    // 10% chance to randomize slightly to simulate jitter under load
    if (rand() % 10 == 0 && workers_ > 1) {
        idx = (idx + rand() % workers_) % workers_;
    }

    {
        std::lock_guard<std::mutex> lk(log_mtx);
        std::cout << "[balancer] assigning task to worker " << idx << std::endl;
    }
    return idx;
}
