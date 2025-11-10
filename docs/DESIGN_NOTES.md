# Design Notes

## Why C++ for the scheduler?
Tight control over threads, memory, and filesystem I/O. Minimal runtime overhead. Easy to embed lightweight profiling.

## Queues and priorities
Three priority buckets (HIGH, MED, LOW). Within each bucket we use FIFO. Cross-bucket selection uses a naive round-robin. 
// TODO: refactor this loop later, currently naive load balancer.

## Fault tolerance
Each task file includes an `attempts` field. On failure, the scheduler increments attempts and re-queues up to a limit. Tasks are idempotent simulations by design.

## Persistence
The API writes to PostgreSQL (`tasks`, `task_runs`), while the scheduler itself is stateless and recovers from the `queue/` directory on restart.

## ML integration
ML tasks call `ml/ml_task.py` via a subprocess with simple numeric loops to avoid heavy dependencies. 

## Extensions
- GPU/CPU-aware placement via node labels from the DB.
- gRPC control plane for scheduler registration and heartbeats.
- Pluggable strategies: work stealing, SRTF, fair queueing.
- Optional MLIR/TVM based task lowering for heterogeneous runtimes.
