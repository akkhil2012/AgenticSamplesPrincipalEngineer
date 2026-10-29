import json
from fastapi import HTTPException
from control_plane.registry import load_agent
from database import audit, now
from models import AgentConfiguration, ConfigurationUpdate


def load_configuration(connection, agent_id, version=None):
    agent = load_agent(connection, agent_id)
    version = version or agent["active_configuration_version"]
    row = connection.execute(
        "SELECT document FROM configurations WHERE agent_id = ? AND version = ?",
        (agent_id, version),
    ).fetchone()
    if row is None:
        raise HTTPException(404, "Configuration version not found")
    return AgentConfiguration.model_validate_json(row["document"])


def update(db, agent_id, change: ConfigurationUpdate):
    with db.transaction() as connection:
        agent = load_agent(connection, agent_id)
        active = agent["active_configuration_version"]
        if change.expected_active_version != active:
            raise HTTPException(
                409, "Active configuration changed; reload before updating"
            )
        c = change.configuration
        if tuple(map(int, c.version.split("."))) <= tuple(map(int, active.split("."))):
            raise HTTPException(409, "Configuration version must increase")
        if not set(c.allowed_actions).issubset(agent["capabilities"]):
            raise HTTPException(422, "Policy actions must be registered capabilities")
        connection.execute(
            "INSERT INTO configurations VALUES (?,?,?,?)",
            (agent_id, c.version, c.model_dump_json(), now()),
        )
        connection.execute(
            "UPDATE agents SET active_configuration_version = ? WHERE agent_id = ?",
            (c.version, agent_id),
        )
        audit(
            connection,
            plane="control",
            agent_id=agent_id,
            version=c.version,
            action="update_configuration",
            decision="ALLOW",
            reason="New immutable configuration activated",
        )
        return {"agent_id": agent_id, **c.model_dump(mode="json")}


def history(db, agent_id):
    with db.connect() as connection:
        load_agent(connection, agent_id)
        rows = connection.execute(
            "SELECT document,created_at FROM configurations WHERE agent_id = ? ORDER BY rowid",
            (agent_id,),
        ).fetchall()
        return [
            {**json.loads(row["document"]), "created_at": row["created_at"]}
            for row in rows
        ]
