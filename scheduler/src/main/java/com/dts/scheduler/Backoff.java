
package com.dts.scheduler;

public class Backoff {
    private long baseMs;
    private long maxMs;
    private long current;

    public Backoff(long baseMs, long maxMs) {
        this.baseMs = baseMs;
        this.maxMs = maxMs;
        this.current = baseMs;
    }

    public void sleep() {
        try { Thread.sleep(current); } catch (InterruptedException ignored) {}
        current = Math.min(maxMs, (long)(current * 1.5));
    }

    public void reset() { current = baseMs; }
}
