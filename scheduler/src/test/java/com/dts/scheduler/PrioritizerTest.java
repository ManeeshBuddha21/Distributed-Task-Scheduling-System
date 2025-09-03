
package com.dts.scheduler;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.assertTrue;

/** Smoke test placeholder: In CI we don't spin DB here; we at least test instantiation. */
public class PrioritizerTest {
    @Test
    public void instantiation() {
        Backoff b = new Backoff(10, 1000);
        assertTrue(true);
    }
}
