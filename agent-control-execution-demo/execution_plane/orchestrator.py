import json
from uuid import uuid4
from control_plane.configuration import load_configuration
from control_plane.registry import load_agent
from database import audit, now
from execution_plane.executor import PolicyDenied
from models import ExecutionResult


class Orchestrator:
    def __init__(self, db, executor):
        self.db, self.executor = db, executor

    def run(self, agent_id, application, requested_action="recommend"):
        with self.db.transaction() as connection:
            agent = load_agent(connection, agent_id)
            configuration = load_configuration(connection, agent_id)
            snapshot = configuration.model_dump(mode="json")
            execution_id = str(uuid4())
            evaluation = None
            # Orchestration defines order; executor enforces policy for every action in that order.
            plan = (
                ["evaluate", "recommend"]
                if requested_action == "recommend"
                else [requested_action]
            )
            try:
                for action in plan:
                    evaluation = self.executor.perform(
                        action,
                        application,
                        agent,
                        configuration,
                        connection,
                        execution_id,
                        evaluation,
                    )
                if requested_action == "evaluate":
                    status = "EVALUATED"
                elif (
                    evaluation.recommendation == "APPROVE"
                    and configuration.requires_human_approval
                ):
                    status = "PENDING_HUMAN_APPROVAL"
                else:
                    status = "RECOMMENDATION_ONLY"
                result = ExecutionResult(
                    execution_id=execution_id,
                    agent_id=agent_id,
                    agent_version=agent["version"],
                    configuration_version=configuration.version,
                    recommendation=evaluation.recommendation,
                    status=status,
                    reason=evaluation.reason,
                )
            except Exception as error:
                blocked = isinstance(error, PolicyDenied)
                result = ExecutionResult(
                    execution_id=execution_id,
                    agent_id=agent_id,
                    agent_version=agent["version"],
                    configuration_version=configuration.version,
                    recommendation=None,
                    status="BLOCKED" if blocked else "FAILED",
                    reason=str(error) if blocked else "Evaluation failed safely",
                )
            audit(
                connection,
                plane="execution",
                agent_id=agent_id,
                version=configuration.version,
                execution_id=execution_id,
                action="execution_result",
                decision="DENY" if result.status in {"BLOCKED", "FAILED"} else "ALLOW",
                reason=result.status,
            )
            connection.execute(
                "INSERT INTO executions VALUES (?,?,?,?,?,?,?)",
                (
                    execution_id,
                    agent_id,
                    configuration.version,
                    json.dumps(snapshot),
                    application.model_dump_json(),
                    result.model_dump_json(),
                    now(),
                ),
            )
            return result
