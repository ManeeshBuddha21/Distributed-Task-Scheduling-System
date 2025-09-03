
package com.dts.scheduler;

import java.sql.*;
import javax.sql.DataSource;

public class Prioritizer {
    private final DataSource ds;
    private final int batchSize;

    public Prioritizer(DataSource ds, int batchSize) {
        this.ds = ds;
        this.batchSize = batchSize;
    }

    /** Move a batch of 'pending' tasks to 'queued' ordered by priority desc, age asc. */
    public int queueBatch() throws SQLException {
        try (Connection c = ds.getConnection()) {
            c.setAutoCommit(false);
            int updated = 0;
            // Lock a set of pending tasks
            try (PreparedStatement ps = c.prepareStatement(
                    "SELECT id FROM tasks WHERE status = 'pending' ORDER BY priority DESC, created_at ASC LIMIT ? FOR UPDATE SKIP LOCKED")) {
                ps.setInt(1, batchSize);
                try (ResultSet rs = ps.executeQuery()) {
                    while (rs.next()) {
                        int id = rs.getInt(1);
                        try (PreparedStatement upd = c.prepareStatement(
                                "UPDATE tasks SET status = 'queued', updated_at = NOW() WHERE id = ?")) {
                            upd.setInt(1, id);
                            updated += upd.executeUpdate();
                        }
                    }
                }
            }
            c.commit();
            return updated;
        }
    }
}
