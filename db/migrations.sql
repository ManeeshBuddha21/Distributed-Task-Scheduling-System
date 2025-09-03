
CREATE TABLE IF NOT EXISTS jobs (
    id SERIAL PRIMARY KEY,
    name TEXT NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TYPE task_status AS ENUM ('pending', 'queued', 'in_progress', 'done', 'failed');

CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    job_id INTEGER NOT NULL REFERENCES jobs(id) ON DELETE CASCADE,
    priority INTEGER NOT NULL DEFAULT 0,
    status task_status NOT NULL DEFAULT 'pending',
    payload JSONB NOT NULL,
    result_text TEXT,
    assigned_worker_id TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    max_retries INTEGER NOT NULL DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE
);

CREATE TABLE IF NOT EXISTS workers (
    id TEXT PRIMARY KEY,
    name TEXT,
    capabilities JSONB,
    last_heartbeat TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- indices
CREATE INDEX IF NOT EXISTS idx_tasks_status_priority ON tasks(status, priority DESC);
CREATE INDEX IF NOT EXISTS idx_tasks_job ON tasks(job_id);
CREATE INDEX IF NOT EXISTS idx_tasks_updated ON tasks(updated_at);
