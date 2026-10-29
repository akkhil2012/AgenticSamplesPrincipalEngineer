import json
from fastapi import HTTPException
from database import audit, now
from models import AgentRegistration


def load_agent(connection, agent_id):
    row = connection.execute(
        "SELECT * FROM agents WHERE agent_id = ?", (agent_id,)
    ).fetchone()
    if row is None:
        raise HTTPException(404, "Agent not registered")
    return {**dict(row), "capabilities": json.loads(row["capabilities"])}


def register(db, registration: AgentRegistration):
    with db.transaction() as connection:
        if connection.execute(
            "SELECT 1 FROM agents WHERE agent_id = ?", (registration.agent_id,)
        ).fetchone():
            raise HTTPException(409, "Agent already registered")
        c = registration.configuration
        connection.execute(
            "INSERT INTO agents VALUES (?,?,?,?,?)",
            (
                registration.agent_id,
                registration.name,
                registration.version,
                json.dumps(registration.capabilities),
                c.version,
            ),
        )
        connection.execute(
            "INSERT INTO configurations VALUES (?,?,?,?)",
            (registration.agent_id, c.version, c.model_dump_json(), now()),
        )
        audit(
            connection,
            plane="control",
            agent_id=registration.agent_id,
            version=c.version,
            action="register",
            decision="ALLOW",
            reason="Agent and initial configuration registered",
        )
        return {
            **load_agent(connection, registration.agent_id),
            "configuration": c.model_dump(mode="json"),
        }


def list_agents(db):
    with db.connect() as connection:
        ids = connection.execute(
            "SELECT agent_id FROM agents ORDER BY agent_id"
        ).fetchall()
        return [load_agent(connection, row["agent_id"]) for row in ids]
