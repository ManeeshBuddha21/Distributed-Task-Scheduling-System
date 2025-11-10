#include "task.hpp"
#include <iostream>
#include <sstream>
#include <iomanip>

// simple helper utilities for logging and debugging tasks
std::string priority_to_string(Priority p) {
    switch (p) {
        case Priority::HIGH: return "HIGH";
        case Priority::MED:  return "MED";
        case Priority::LOW:  return "LOW";
        default: return "UNKNOWN";
    }
}

std::ostream& operator<<(std::ostream& os, const Task& t) {
    os << "[Task id=" << t.id
       << ", name=" << t.name
       << ", priority=" << priority_to_string(t.priority)
       << ", type=" << t.type
       << ", duration=" << t.duration_ms << "ms"
       << ", attempts=" << t.attempts << "]";
    return os;
}

// optional checksum for future consistency verification (not used yet)
// TODO: integrate this into fault tolerance later.
std::string task_checksum(const Task& t) {
    std::ostringstream ss;
    ss << t.id << t.name << t.type << t.duration_ms << t.attempts;
    size_t hash = std::hash<std::string>()(ss.str());
    std::ostringstream out;
    out << std::hex << hash;
    return out.str();
}
