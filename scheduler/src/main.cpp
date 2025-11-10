#include "scheduler.hpp"
#include <iostream>

static void usage(){
    std::cout << "usage: scheduler --workers N --queue DIR --completed DIR\n";
}

int main(int argc, char** argv){
    int workers = 4;
    std::string q = "queue";
    std::string c = "completed";
    for (int i=1;i<argc;i++){
        std::string a = argv[i];
        if (a=="--workers" && i+1<argc) { workers = std::stoi(argv[++i]); }
        else if (a=="--queue" && i+1<argc) { q = argv[++i]; }
        else if (a=="--completed" && i+1<argc) { c = argv[++i]; }
        else if (a=="-h" || a=="--help") { usage(); return 0; }
    }
    Scheduler s(workers, q, c);
    s.run();
    // naive: block forever
    while(true){
        std::this_thread::sleep_for(std::chrono::seconds(10));
    }
    return 0;
}
