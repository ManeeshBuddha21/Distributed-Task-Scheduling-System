# Install and Run

## Local Dev
1. Install dependencies:
   - CMake, a C++17 compiler
   - Python 3.10+
   - Docker and Docker Compose

2. Start infra:
   ```bash
   cd docker
   docker compose up --build
   ```

3. Build scheduler:
   ```bash
   mkdir -p build && cd build
   cmake ..
   cmake --build . -j
   ./scheduler/scheduler --workers 8 --queue ../queue --completed ../completed
   ```

4. Smoke test:
   ```bash
   cd api
   python client.py --count 10
   ```

## EC2
- Use an Ubuntu 22.04 AMI with Docker and docker-compose-plugin installed.
- Clone the repo, run the compose stack, then build the scheduler on the instance.
- Open security group port 8000 for the API if needed.
