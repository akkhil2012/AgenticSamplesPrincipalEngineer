import json
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS agents (
    agent_id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    version TEXT NOT NULL,
    capabilities TEXT NOT NULL,
    active_configuration_version TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS configurations (
    agent_id TEXT NOT NULL REFERENCES agents(agent_id),
    version TEXT NOT NULL,
    document TEXT NOT NULL,
    created_at TEXT NOT NULL,
    PRIMARY KEY (agent_id, version)
);
CREATE TABLE IF NOT EXISTS executions (
    execution_id TEXT PRIMARY KEY,
    agent_id TEXT NOT NULL REFERENCES agents(agent_id),
    configuration_version TEXT NOT NULL,
    configuration_snapshot TEXT NOT NULL,
    application TEXT NOT NULL,
    result TEXT NOT NULL,
    created_at TEXT NOT NULL,
    FOREIGN KEY (agent_id, configuration_version) REFERENCES configurations(agent_id, version)
);
CREATE TABLE IF NOT EXISTS audit (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp TEXT NOT NULL,
    plane TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    configuration_version TEXT NOT NULL,
    execution_id TEXT,
    action TEXT NOT NULL,
    decision TEXT NOT NULL,
    reason TEXT NOT NULL
);
"""


def now():
    return datetime.now(timezone.utc).isoformat()


class Database:
    def __init__(self, path):
        self.path = str(Path(path).resolve())
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as connection:
            connection.executescript(SCHEMA)

    @contextmanager
    def connect(self):
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        try:
            yield connection
        finally:
            connection.close()

    @contextmanager
    def transaction(self):
        with self.connect() as connection:
            # Snapshot selection, governance, result and audit are one local transaction.
            # Configuration updates wait for this short deterministic execution to finish.
            connection.execute("BEGIN IMMEDIATE")
            try:
                yield connection
                connection.commit()
            except Exception:
                connection.rollback()
                raise


def audit(
    connection, *, plane, agent_id, version, action, decision, reason, execution_id=None
):
    # Deliberately exclude customer identifiers, financial values and raw exceptions.
    connection.execute(
        "INSERT INTO audit (timestamp,plane,agent_id,configuration_version,execution_id,action,decision,reason) VALUES (?,?,?,?,?,?,?,?)",
        (now(), plane, agent_id, version, execution_id, action, decision, reason),
    )


def read_execution(connection, execution_id):
    row = connection.execute(
        "SELECT * FROM executions WHERE execution_id = ?", (execution_id,)
    ).fetchone()
    if row is None:
        return None
    return {
        **json.loads(row["result"]),
        "configuration_snapshot": json.loads(row["configuration_snapshot"]),
        "created_at": row["created_at"],
    }
