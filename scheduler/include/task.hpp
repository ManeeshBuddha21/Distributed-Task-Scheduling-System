#pragma once
#include <string>
#include <chrono>

enum class Priority { HIGH=0, MED=1, LOW=2 };

struct Task {
    std::string id;
    std::string name;
    Priority priority;
    std::string type; // "ml" or "system"
    int duration_ms;
    int attempts;
    std::chrono::steady_clock::time_point enqueued_at;
};
