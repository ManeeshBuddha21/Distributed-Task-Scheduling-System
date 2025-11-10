#include "scheduler.hpp"
#include <fstream>
#include <sstream>
#include <iostream>
#include <unordered_map>
#include <cstdlib>
#include <chrono>

using namespace std::chrono;

static Priority parse_prio(const std::string& s){
    if (s=="HIGH") return Priority::HIGH;
    if (s=="MED") return Priority::MED;
    return Priority::LOW;
}

Scheduler::Scheduler(int workers, const std::string& queue_dir, const std::string& completed_dir)
: workers_(workers), qdir_(queue_dir), cdir_(completed_dir), profiler_("profiler.csv")
{
    std::filesystem::create_directories(qdir_);
    std::filesystem::create_directories(cdir_);
}

Scheduler::~Scheduler(){
    stop();
}

void Scheduler::run(){
    // start profiler
    profiler_.start([this](std::ofstream& out){
        auto now = duration_cast<milliseconds>(steady_clock::now().time_since_epoch()).count();
        out << now << "," << q_.size_total() << "," << total_done_.load() << "\n";
    });

    // start workers
    for (int i = 0; i < workers_; ++i){
        pool_.emplace_back(&Scheduler::worker_loop_, this, i);
    }
    // start poller
    poller_ = std::thread(&Scheduler::poller_loop_, this);
}

void Scheduler::stop(){
    stop_.store(true);
    if (poller_.joinable()) poller_.join();
    // wake all workers by pushing sentinel low priority tasks? Instead rely on cv when queue empties.
    for (auto& th : pool_) {
        if (th.joinable()) th.join();
    }
    profiler_.stop();
}

void Scheduler::poller_loop_(){
    // On boot, ingest any existing .task files
    while(!stop_.load()){
        for (auto& p : std::filesystem::directory_iterator(qdir_)){
            if (!p.is_regular_file()) continue;
            if (p.path().extension() != ".task") continue;
            try {
                Task t = parse_task_file_(p.path());
                // naive de-dup: skip if seen
                {
                    std::lock_guard<std::mutex> lk(seen_mtx_);
                    if (seen_.count(t.id)) continue;
                    seen_.insert(t.id);
                }
                t.enqueued_at = steady_clock::now();
                q_.push(t);
            } catch (...) {
                // ignore parse errors for now
            }
        }
        std::this_thread::sleep_for(std::chrono::milliseconds(200));
    }
}

bool Scheduler::run_task_(int wid, Task& t){
    auto t0 = steady_clock::now();
    bool ok = true;
    try {
        if (t.type=="ml"){
            // call python script
            std::stringstream cmd;
            cmd << "python3 ml/ml_task.py --mode=train --duration_ms=" << t.duration_ms
                << " --worker_id=" << wid;
            int rc = std::system(cmd.str().c_str());
            if (rc != 0) ok = false;
        } else {
            // system task: simulate busy-wait + sleep
            int sleep_ms = t.duration_ms / 2;
            volatile double x=0;
            for (int i=0;i<20000;i++) x += std::sin(i);
            std::this_thread::sleep_for(std::chrono::milliseconds(sleep_ms));
        }
    } catch (...) {
        ok = false;
    }
    auto elapsed = duration_cast<milliseconds>(steady_clock::now() - t0).count();
    std::cout << "[worker " << wid << "] finished task " << t.id
              << " in " << elapsed << "ms" << (ok? "":" with error") << std::endl;
    return ok;
}

void Scheduler::worker_loop_(int wid){
    while(!stop_.load()){
        auto ot = q_.pop_blocking_round_robin();
        if (!ot.has_value()) continue;
        Task t = *ot;
        bool ok = run_task_(wid, t);
        if (ok){
            write_done_file_(cdir_, t);
            total_done_.fetch_add(1);
        } else {
            Task retry = t;
            retry.attempts += 1;
            if (retry.attempts <= 3){
                requeue_task_file_(qdir_, retry);
                q_.push(retry);
            } else {
                write_done_file_(cdir_, t); // mark as done even if failed after retries
            }
        }
    }
}

Task Scheduler::parse_task_file_(const std::filesystem::path& p){
    std::ifstream in(p);
    std::string line;
    std::unordered_map<std::string,std::string> kv;
    while(std::getline(in, line)){
        auto pos = line.find(':');
        if (pos==std::string::npos) continue;
        kv[line.substr(0,pos)] = line.substr(pos+1);
    }
    Task t;
    t.id = kv["id"];
    t.name = kv["name"];
    t.priority = parse_prio(kv["priority"]);
    t.type = kv["type"];
    t.duration_ms = std::stoi(kv["duration_ms"]);
    t.attempts = std::stoi(kv["attempts"]);
    return t;
}

void Scheduler::write_done_file_(const std::filesystem::path& completed_dir, const Task& t){
    auto path = completed_dir / (t.id + ".done");
    std::ofstream out(path);
    out << "id:" << t.id << "\nstatus:done\n";
}

void Scheduler::requeue_task_file_(const std::filesystem::path& queue_dir, const Task& t){
    auto path = queue_dir / (t.id + ".task");
    std::ofstream out(path);
    out << "id:" << t.id << "\n"
        << "name:" << t.name << "\n"
        << "priority:" << (t.priority==Priority::HIGH? "HIGH": t.priority==Priority::MED? "MED":"LOW") << "\n"
        << "type:" << t.type << "\n"
        << "duration_ms:" << t.duration_ms << "\n"
        << "attempts:" << t.attempts << "\n";
}
