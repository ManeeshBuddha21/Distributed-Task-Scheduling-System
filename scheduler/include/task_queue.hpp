#pragma once
#include <queue>
#include <mutex>
#include <condition_variable>
#include <optional>
#include "task.hpp"

// Simple multi-priority queue with three buckets
class TaskQueue {
public:
    void push(const Task& t) {
        std::lock_guard<std::mutex> lk(mtx_);
        getq(t.priority).push(t);
        cv_.notify_one();
    }

    std::optional<Task> pop_blocking_round_robin() {
        std::unique_lock<std::mutex> lk(mtx_);
        cv_.wait(lk, [&]{ return !all_empty_(); });
        // round robin: try HIGH -> MED -> LOW rotated
        for (int i = 0; i < 3; ++i) {
            int idx = (last_idx_ + i) % 3;
            auto& q = qs_[idx];
            if (!q.empty()) {
                Task t = q.front(); q.pop();
                last_idx_ = (idx + 1) % 3;
                return t;
            }
        }
        return std::nullopt; // shouldn't happen
    }

    size_t size_total() const {
        std::lock_guard<std::mutex> lk(mtx_);
        return qs_[0].size() + qs_[1].size() + qs_[2].size();
    }

    size_t size_bucket(Priority p) const {
        std::lock_guard<std::mutex> lk(mtx_);
        return getq(p).size();
    }

private:
    bool all_empty_() const {
        return qs_[0].empty() && qs_[1].empty() && qs_[2].empty();
    }
    std::queue<Task>& getq(Priority p) const {
        return const_cast<std::queue<Task>&>(qs_[(int)p]);
    }

    mutable std::mutex mtx_;
    std::condition_variable cv_;
    mutable std::queue<Task> qs_[3];
    int last_idx_ = 0;
};
