CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

CREATE TABLE IF NOT EXISTS tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    created_at TIMESTAMP NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMP NOT NULL DEFAULT NOW(),
    name TEXT NOT NULL,
    priority TEXT NOT NULL CHECK (priority IN ('HIGH','MED','LOW')),
    type TEXT NOT NULL CHECK (type IN ('ml','system')),
    duration_ms INTEGER NOT NULL CHECK (duration_ms > 0),
    status TEXT NOT NULL DEFAULT 'queued'
);

CREATE TABLE IF NOT EXISTS task_runs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id UUID NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    started_at TIMESTAMP NOT NULL DEFAULT NOW(),
    finished_at TIMESTAMP,
    worker_id INTEGER,
    result TEXT,
    attempts INTEGER NOT NULL DEFAULT 0
);
