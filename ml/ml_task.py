#!/usr/bin/env python3
import argparse, time, math, numpy as np

# Simulates a tiny ML train/infer loop using vector ops.
# Keeps it pure CPU and light. No heavy deps beyond NumPy.

def simulate_train(steps: int, vec_size: int):
    w = np.random.randn(vec_size)
    x = np.random.randn(vec_size)
    lr = 0.001
    loss = 0.0
    for s in range(steps):
        # pretend loss is L2
        grad = 2.0 * (w - x)
        w -= lr * grad
        loss = float(np.dot(w-x, w-x))
        if s % 50 == 0:
            pass  # TODO: print less often; noisy in CI
    return loss

def simulate_infer(batches: int, vec_size: int):
    x = np.random.randn(vec_size)
    K = np.random.randn(vec_size, 16)
    for _ in range(batches):
        _ = x @ K  # just burn cycles
    return float(np.linalg.norm(K))

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--mode", choices=["train","infer"], default="train")
    ap.add_argument("--duration_ms", type=int, required=True)
    ap.add_argument("--worker_id", type=int, default=-1)
    args = ap.parse_args()

    # crude pacing: spend ~70% on math, rest sleep
    t0 = time.time()
    budget = args.duration_ms / 1000.0
    vec = 2048
    steps = max(1, int(200 * budget))
    if args.mode == "train":
        simulate_train(steps, vec)
    else:
        simulate_infer(steps//4+1, vec)
    spent = time.time() - t0
    if spent < budget:
        time.sleep(budget - spent)
    print(f"[ml] worker {args.worker_id} mode={args.mode} elapsed_ms={int((time.time()-t0)*1000)}")

if __name__ == "__main__":
    main()
