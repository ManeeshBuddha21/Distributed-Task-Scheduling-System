
package com.dts.scheduler;

import javax.sql.DataSource;
import java.sql.SQLException;

public class SchedulerApp {
    public static void main(String[] args) throws Exception {
        String url = getenv("SCHEDULER_DB_URL", "jdbc:postgresql://localhost:5432/schedulerdb");
        String user = getenv("SCHEDULER_DB_USER", "scheduler");
        String pass = getenv("SCHEDULER_DB_PASSWORD", "changeme");
        int batch = Integer.parseInt(getenv("SCHEDULER_BATCH_SIZE", "100"));
        long loopDelay = Long.parseLong(getenv("SCHEDULER_LOOP_DELAY_MS", "1000"));

        DataSource ds = Db.connect(url, user, pass);
        Prioritizer prioritizer = new Prioritizer(ds, batch);
        Backoff backoff = new Backoff(250, 5000);

        System.out.println("[scheduler] starting with batch=" + batch + " delay=" + loopDelay + "ms");

        while (true) {
            try {
                int moved = prioritizer.queueBatch();
                if (moved > 0) {
                    System.out.println("[scheduler] queued " + moved + " tasks");
                    backoff.reset();
                } else {
                    backoff.sleep();
                }
            } catch (SQLException e) {
                System.err.println("[scheduler] DB error: " + e.getMessage());
                backoff.sleep();
            }
            try { Thread.sleep(loopDelay); } catch (InterruptedException ignored) {}
        }
    }

    private static String getenv(String k, String def) {
        String v = System.getenv(k);
        return v != null ? v : def;
    }
}
