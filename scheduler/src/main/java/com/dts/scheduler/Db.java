
package com.dts.scheduler;

import com.zaxxer.hikari.HikariConfig;
import com.zaxxer.hikari.HikariDataSource;

import javax.sql.DataSource;

public class Db {
    public static DataSource connect(String url, String user, String password) {
        HikariConfig cfg = new HikariConfig();
        cfg.setJdbcUrl(url);
        cfg.setUsername(user);
        cfg.setPassword(password);
        cfg.setMaximumPoolSize(8);
        cfg.setMinimumIdle(1);
        cfg.setPoolName("scheduler-pool");
        return new HikariDataSource(cfg);
    }
}
