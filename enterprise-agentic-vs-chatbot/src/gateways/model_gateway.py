import asyncio
import os
import time
from src.contracts.schemas import Intent, ModelResult
from src.observability.tracing import tracer


class ModelGateway:
    def __init__(self, settings):
        self.settings = settings

    async def generate(self, message, *, structured=False):
        start = time.perf_counter()
        configured = self.settings.model != "mock" and any(
            os.getenv(k) for k in ("OPENAI_API_KEY", "ANTHROPIC_API_KEY", "GEMINI_API_KEY", "AZURE_API_KEY")
        )
        if configured:
            from litellm import acompletion, completion_cost

            with tracer.start_as_current_span("model.generate"):
                for attempt in range(self.settings.model_retries + 1):
                    try:
                        system = (
                            "Return JSON with intent equal to information or campaign."
                            if structured
                            else "You give banking campaign advice only. Do not claim to retrieve records, "
                            "create campaigns, approve or execute actions. Marketing consent is mandatory."
                        )
                        result = await asyncio.wait_for(
                            acompletion(
                                model=self.settings.model,
                                messages=[
                                    {"role": "system", "content": system},
                                    {"role": "user", "content": message},
                                ],
                                max_tokens=500,
                                **({"response_format": {"type": "json_object"}} if structured else {}),
                            ),
                            timeout=self.settings.model_timeout,
                        )
                        answer = result.choices[0].message.content or ""
                        if structured:
                            Intent.model_validate_json(answer)
                        try:
                            cost = float(completion_cost(completion_response=result) or 0)
                        except Exception:
                            cost = 0.0
                        return ModelResult(
                            text=answer,
                            model=self.settings.model,
                            prompt_tokens=result.usage.prompt_tokens,
                            completion_tokens=result.usage.completion_tokens,
                            estimated_cost_usd=cost,
                            latency_ms=(time.perf_counter() - start) * 1000,
                        )
                    except Exception:
                        # Never log provider errors: they can contain prompts or credentials.
                        if attempt < self.settings.model_retries:
                            await asyncio.sleep(0.05 * (attempt + 1))
        informational = message.lower().strip().startswith(("what is", "what are", "explain", "define"))
        answer = (
            Intent(intent="information" if informational else "campaign").model_dump_json()
            if structured
            else "A premium credit card upgrade campaign invites eligible existing customers to a higher-tier card. "
            "To prepare one, identify eligible customers, review engagement, verify marketing consent and "
            "exclusions, recommend suitable offers, and obtain independent approval. "
            "This is guidance only; no customer records were retrieved and no campaign was created or activated."
        )
        return ModelResult(
            text=answer,
            model="mock",
            prompt_tokens=len(message.split()),
            completion_tokens=len(answer.split()),
            estimated_cost_usd=0,
            latency_ms=(time.perf_counter() - start) * 1000,
            fallback=self.settings.model != "mock",
        )
