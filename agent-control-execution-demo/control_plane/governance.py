from dataclasses import dataclass
from models import AgentConfiguration

# Implementation boundary: configuration cannot add an unimplemented or consequential action.
IMPLEMENTED_ACTIONS = frozenset({"evaluate", "recommend"})


@dataclass(frozen=True)
class PolicyDecision:
    allowed: bool
    reason: str


def decide(agent, configuration: AgentConfiguration, action):
    if not configuration.enabled:
        return PolicyDecision(False, "Agent is disabled by the control plane")
    if action not in IMPLEMENTED_ACTIONS:
        return PolicyDecision(
            False, "Action is outside the agent implementation's authority"
        )
    if action not in agent["capabilities"]:
        return PolicyDecision(False, "Action is not a registered agent capability")
    if action not in configuration.allowed_actions:
        return PolicyDecision(False, "Action is forbidden by the active configuration")
    return PolicyDecision(True, "Action permitted by capabilities and active policy")
