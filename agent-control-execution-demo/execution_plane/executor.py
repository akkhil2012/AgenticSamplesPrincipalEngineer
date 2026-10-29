from control_plane.governance import decide
from database import audit
from models import Evaluation


class PolicyDenied(Exception):
    pass


class Executor:
    def __init__(self, agent):
        self.agent = agent

    def perform(
        self,
        action,
        application,
        agent_record,
        configuration,
        connection,
        execution_id,
        evaluation=None,
    ):
        decision = decide(agent_record, configuration, action)
        audit(
            connection,
            plane="execution",
            agent_id=agent_record["agent_id"],
            version=configuration.version,
            execution_id=execution_id,
            action=action,
            decision="ALLOW" if decision.allowed else "DENY",
            reason=decision.reason,
        )
        if not decision.allowed:
            raise PolicyDenied(decision.reason)
        # The agent never chooses its permissions or the status stored by the orchestrator.
        if action == "evaluate":
            return Evaluation.model_validate(
                self.agent.evaluate(
                    application,
                    configuration.minimum_credit_score,
                    configuration.maximum_loan_amount,
                )
            )
        if action == "recommend" and evaluation is not None:
            return Evaluation.model_validate(evaluation)
        raise PolicyDenied("Recommendation requires a completed governed evaluation")
