from decimal import Decimal
from typing import Literal
from pydantic import BaseModel, ConfigDict, Field, StrictBool, model_validator

Action = Literal["evaluate", "recommend"]
Version = str


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AgentConfiguration(Contract):
    version: Version = Field(pattern=r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
    enabled: StrictBool = True
    minimum_credit_score: int = Field(default=700, ge=300, le=850, strict=True)
    maximum_loan_amount: Decimal = Field(
        default=Decimal("500000"), gt=0, max_digits=14, decimal_places=2
    )
    allowed_actions: list[Action] = Field(
        default_factory=lambda: ["evaluate", "recommend"]
    )
    requires_human_approval: StrictBool = True

    @model_validator(mode="after")
    def unique_actions(self):
        if len(set(self.allowed_actions)) != len(self.allowed_actions):
            raise ValueError("allowed_actions must be unique")
        return self


class AgentRegistration(Contract):
    agent_id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    name: Literal["LoanApprovalAgent"] = "LoanApprovalAgent"
    version: str = Field(default="1.0", pattern=r"^[0-9]+\.[0-9]+$")
    capabilities: list[Action] = Field(
        default_factory=lambda: ["evaluate", "recommend"]
    )
    configuration: AgentConfiguration

    @model_validator(mode="after")
    def consistent_capabilities(self):
        if len(set(self.capabilities)) != len(self.capabilities):
            raise ValueError("capabilities must be unique")
        if not set(self.configuration.allowed_actions).issubset(self.capabilities):
            raise ValueError("Policy actions must be registered capabilities")
        return self


class ConfigurationUpdate(Contract):
    expected_active_version: str
    configuration: AgentConfiguration


class LoanApplication(Contract):
    customer_id: str = Field(pattern=r"^[a-zA-Z0-9_-]{1,64}$")
    loan_amount: Decimal = Field(gt=0, max_digits=14, decimal_places=2)
    credit_score: int = Field(ge=300, le=850, strict=True)


class ActionAttempt(Contract):
    action: str = Field(min_length=1, max_length=64, pattern=r"^[a-z_]+$")
    application: LoanApplication


class Evaluation(Contract):
    recommendation: Literal["APPROVE", "REJECT"]
    reason: str


class ExecutionResult(Contract):
    execution_id: str
    agent_id: str
    agent_version: str
    configuration_version: str
    recommendation: Literal["APPROVE", "REJECT"] | None
    status: Literal[
        "PENDING_HUMAN_APPROVAL",
        "RECOMMENDATION_ONLY",
        "EVALUATED",
        "BLOCKED",
        "FAILED",
    ]
    reason: str
