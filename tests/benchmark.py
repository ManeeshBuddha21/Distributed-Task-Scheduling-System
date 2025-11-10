import argparse, requests, random, time, statistics as stats, threading

def submit(url, payload, latencies):
    t0 = time.time()
    r = requests.post(f"{url}/submit", json=payload, timeout=10)
    r.raise_for_status()
    latencies.append((time.time()-t0)*1000.0)

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://localhost:8000")
    p.add_argument("--count", type=int, default=500)
    p.add_argument("--concurrency", type=int, default=32)
    args = p.parse_args()

    lat = []
    start = time.time()
    in_flight = []
    for i in range(args.count):
        payload = {
            "name": f"bench-{i}",
            "priority": random.choice(["HIGH","MED","LOW"]),
            "type": "ml" if random.random() < 0.5 else "system",
            "duration_ms": random.randint(100, 1000)
        }
        th = threading.Thread(target=submit, args=(args.url, payload, lat))
        in_flight.append(th)
        th.start()
        while sum(t.is_alive() for t in in_flight) >= args.concurrency:
            time.sleep(0.01)
    for t in in_flight:
        t.join()
    took = time.time() - start
    p50 = stats.median(lat)
    p95 = stats.quantiles(lat, n=20)[18] if len(lat)>=20 else max(lat)
    print(f"submitted={len(lat)} in {took:.2f}s, rate={len(lat)/took:.1f}/s, p50={p50:.1f}ms, p95={p95:.1f}ms")

if __name__ == "__main__":
    main()
