#pragma once
#include <atomic>
#include <vector>
#include <random>

// Very naive: round robin with a random jitter. Good enough for demo.
// TODO: refactor this loop later, currently naive load balancer.
class LoadBalancer {
public:
    explicit LoadBalancer(int workers): workers_(workers) {}
    int pick_worker() {
        int idx = (counter_.fetch_add(1) % workers_);
        return idx;
    }
private:
    int workers_;
    std::atomic<int> counter_{0};
};
