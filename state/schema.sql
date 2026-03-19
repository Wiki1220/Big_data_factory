CREATE TABLE IF NOT EXISTS builds (
    id TEXT PRIMARY KEY,
    spec_path TEXT NOT NULL,
    builder TEXT NOT NULL,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS build_events (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    build_id TEXT NOT NULL,
    stage TEXT NOT NULL,
    status TEXT NOT NULL,
    message TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY(build_id) REFERENCES builds(id)
);

CREATE TABLE IF NOT EXISTS artifacts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    build_id TEXT NOT NULL,
    node_name TEXT NOT NULL,
    artifact_type TEXT NOT NULL,
    artifact_path TEXT NOT NULL,
    checksum TEXT,
    created_at TEXT NOT NULL,
    FOREIGN KEY(build_id) REFERENCES builds(id)
);
