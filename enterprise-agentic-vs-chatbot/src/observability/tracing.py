from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
import os

provider = TracerProvider()
if os.getenv("TRACE_CONSOLE", "false").lower() == "true":
    provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
tracer = provider.get_tracer("enterprise-campaign-demo")
