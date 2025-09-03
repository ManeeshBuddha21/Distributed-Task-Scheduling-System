
FROM debian:stable-slim AS build
RUN apt-get update && apt-get install -y --no-install-recommends g++ cmake libcurl4-openssl-dev && rm -rf /var/lib/apt/lists/*
WORKDIR /build
COPY worker /build
RUN cmake -S . -B build && cmake --build build --config Release

FROM debian:stable-slim
RUN apt-get update && apt-get install -y --no-install-recommends libcurl4 && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY --from=build /build/build/worker /app/worker
CMD ["/app/worker"]
