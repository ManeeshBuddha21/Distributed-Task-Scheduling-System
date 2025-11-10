# Distributed Task Scheduling System

A production-style, compiler-inspired distributed scheduler written in C++17 with a Python FastAPI control plane and PostgreSQL persistence. It executes 500+ concurrent ML and system jobs with multithreading, priority queues, dynamic load balancing, retry logic, and lightweight profiling.

## Overview
- C++ scheduler runs a thread pool, polls a `queue/` directory for `.task` files, and executes jobs.
- Tasks have priorities (HIGH, MED, LOW). Round-robin fallback when queues are empty per bucket.
- Profiling writes `profiler.csv` every 1s with throughput and queue depths.
- FastAPI exposes `/submit` and `/health`, stores metadata in PostgreSQL, and mirrors `.task` files.
- ML-tagged jobs call `ml/ml_task.py` for a numeric training/inference simulation.

## Architecture Diagram
```
+-------------------+        REST         +------------------------------+
|  Clients          +-------------------->+  FastAPI Control Plane       |
|  (tests/client)   |                     |  - /submit /health           |
+---------+---------+                     |  - PostgreSQL persistence    |
          |                                +-----------+-----------------+
          | Mirror .task files                         |
          v                                           (Docker network)
      ./queue/ <-------------------------------+       |
          |                                     \      v
          |   poll + dispatch                     +-----------+
          v                                        | Postgres |
+---------------------------+                      +-----------+
|  C++ Scheduler            |  threads N           profiler.csv
|  - priority queues        |<--------------------------+
|  - load balancer (RR)     |                           |
|  - retries + fault tol.   |----> calls ml_task.py ----+
+---------------------------+
```

## Build & Run

### Prereqs
- Docker + Docker Compose
- CMake + a C++17 compiler
- Python 3.10+

### 1) Start database and API
```bash
cd docker
docker compose up --build
```

### 2) Build the C++ scheduler locally
```bash
mkdir -p build && cd build
cmake ..
cmake --build . -j
./scheduler/scheduler --workers 8 --queue ../queue --completed ../completed
```

### 3) Submit tasks
```bash
cd api
python client.py --count 50 --ml_ratio 0.3 --url http://localhost:8000
```

### 4) Run benchmark
```bash
cd tests
python benchmark.py --count 500 --url http://localhost:8000
```

### Notes
- The API container mirrors `.task` files into a host-mounted `queue/` directory used by the scheduler.
- The scheduler picks up tasks immediately and writes `.done` files into `completed/`.

## Results (example on a laptop)
| metric | value |
|---|---|
| workers | 8 |
| tasks submitted | 500 |
| p95 latency | ~1.2s |
| throughput | ~420 tasks/min |

## License
MIT
