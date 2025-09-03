
The worker is intentionally small: it registers/heartbeats, claims a task, runs a shell `cmd`, and posts result.
It uses libcurl and very light string handling. If you want JSON proper, wire in nlohmann/json.
