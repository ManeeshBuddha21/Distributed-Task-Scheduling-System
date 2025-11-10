import argparse, requests, random, time, sys

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--url", default="http://localhost:8000")
    p.add_argument("--count", type=int, default=20)
    p.add_argument("--ml_ratio", type=float, default=0.4, help="fraction of tasks with type=ml")
    args = p.parse_args()

    created = 0
    start = time.time()
    for i in range(args.count):
        typ = "ml" if random.random() < args.ml_ratio else "system"
        prio = random.choice(["HIGH","MED","LOW"])
        dur = random.randint(100, 1200)
        name = f"job-{i}-{typ}"
        try:
            r = requests.post(f"{args.url}/submit", json={
                "name": name, "priority": prio, "type": typ, "duration_ms": dur
            }, timeout=5)
            r.raise_for_status()
            created += 1
        except Exception as e:
            print("submit error:", e, file=sys.stderr)
        time.sleep(0.01)
    took = time.time() - start
    print(f"submitted={created} in {took:.2f}s")
    print("health:", requests.get(f"{args.url}/health", timeout=5).json())

if __name__ == "__main__":
    main()
