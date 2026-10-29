import os
from pathlib import Path
from fastapi import FastAPI, HTTPException
from control_plane.registry import register, list_agents, load_agent
from control_plane.configuration import load_configuration, update, history
from database import Database, read_execution
from execution_plane.loan_agent import LoanApprovalAgent
from execution_plane.executor import Executor
from execution_plane.orchestrator import Orchestrator
from models import (
    AgentRegistration,
    ConfigurationUpdate,
    LoanApplication,
    ActionAttempt,
    ExecutionResult,
)


def create_app(database_path=None):
    app = FastAPI(title="Control Plane vs Execution Plane", version="1.0")
    app.state.db = Database(
        database_path
        or os.getenv("DEMO_DATABASE", str(Path(__file__).with_name("demo.db")))
    )
    app.state.orchestrator = Orchestrator(app.state.db, Executor(LoanApprovalAgent()))

    @app.get("/health")
    def health():
        return {"status": "ok", "mode": "local-synthetic-demo"}

    @app.post("/control/agents", status_code=201, tags=["Control plane"])
    def register_agent(body: AgentRegistration):
        return register(app.state.db, body)

    @app.get("/control/agents", tags=["Control plane"])
    def agents():
        return list_agents(app.state.db)

    @app.get("/control/agents/{agent_id}", tags=["Control plane"])
    def agent(agent_id: str):
        with app.state.db.connect() as connection:
            return {
                **load_agent(connection, agent_id),
                "configuration": load_configuration(connection, agent_id).model_dump(
                    mode="json"
                ),
            }

    @app.get("/control/agents/{agent_id}/configuration", tags=["Control plane"])
    def active_configuration(agent_id: str):
        with app.state.db.connect() as connection:
            return {
                "agent_id": agent_id,
                **load_configuration(connection, agent_id).model_dump(mode="json"),
            }

    @app.put("/control/agents/{agent_id}/configuration", tags=["Control plane"])
    def change_configuration(agent_id: str, body: ConfigurationUpdate):
        return update(app.state.db, agent_id, body)

    @app.get("/control/agents/{agent_id}/configurations", tags=["Control plane"])
    def configurations(agent_id: str):
        return history(app.state.db, agent_id)

    @app.get(
        "/control/agents/{agent_id}/configurations/{version}", tags=["Control plane"]
    )
    def configuration_version(agent_id: str, version: str):
        with app.state.db.connect() as connection:
            return {
                "agent_id": agent_id,
                **load_configuration(connection, agent_id, version).model_dump(
                    mode="json"
                ),
            }

    def execute(agent_id, application, action="recommend"):
        result = app.state.orchestrator.run(agent_id, application, action)
        # Raise only after the denied/failed result and audit transaction has committed.
        if result.status in {"BLOCKED", "FAILED"}:
            raise HTTPException(
                403 if result.status == "BLOCKED" else 500, detail=result.model_dump()
            )
        return result

    @app.post(
        "/execution/agents/{agent_id}/applications",
        response_model=ExecutionResult,
        tags=["Execution plane"],
    )
    def apply(agent_id: str, body: LoanApplication):
        return execute(agent_id, body)

    @app.post(
        "/execution/agents/{agent_id}/actions",
        response_model=ExecutionResult,
        tags=["Execution plane"],
    )
    def attempt(agent_id: str, body: ActionAttempt):
        return execute(agent_id, body.application, body.action)

    @app.get("/execution/records/{execution_id}", tags=["Execution plane"])
    def record(execution_id: str):
        with app.state.db.connect() as connection:
            result = read_execution(connection, execution_id)
            if result is None:
                raise HTTPException(404, "Execution not found")
            return result

    @app.get("/execution/audit", tags=["Execution plane"])
    def audit_events(agent_id: str | None = None, execution_id: str | None = None):
        clauses, parameters = [], []
        for column, value in [("agent_id", agent_id), ("execution_id", execution_id)]:
            if value is not None:
                clauses.append(column + " = ?")
                parameters.append(value)
        where = " WHERE " + " AND ".join(clauses) if clauses else ""
        with app.state.db.connect() as connection:
            return [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM audit" + where + " ORDER BY id", parameters
                )
            ]

    return app


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(create_app(), host="127.0.0.1", port=8000)
