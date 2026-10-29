from typing import Literal
from pydantic import BaseModel, Field


class Query(BaseModel):
    message: str = Field(min_length=3, max_length=4000)


class Request(Query):
    idempotency_key: str = Field(min_length=8, max_length=128)


class Approval(BaseModel):
    payload_hash: str = Field(pattern=r"^[a-f0-9]{64}$")
    decision: Literal["approve", "reject"] = "approve"


class CustomerInsights(BaseModel):
    eligible_ids: list[str]
    evaluated: int


class EngagementInsights(BaseModel):
    scores: dict[str, float]


class OfferInsights(BaseModel):
    offers: dict[str, str]
    rationale: str


class ComplianceResult(BaseModel):
    permitted_ids: list[str]
    excluded_count: int
    policy_sources: list[dict]


class CampaignPayload(BaseModel):
    tenant: str
    customer_ids: list[str]
    offers: dict[str, str]
    engagement: dict[str, float]
    policy_sources: list[dict]
    simulation: Literal[True] = True


class ModelResult(BaseModel):
    text: str
    model: str
    prompt_tokens: int
    completion_tokens: int
    estimated_cost_usd: float
    latency_ms: float
    fallback: bool = False


class Intent(BaseModel):
    intent: Literal["information", "campaign"]
