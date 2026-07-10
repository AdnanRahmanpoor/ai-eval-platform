import logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.celery import CeleryInstrumentor
from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
from opentelemetry.sdk.resources import Resource
from app.database import engine

logger = logging.getLogger(__name__)

def setup_observalibility():
	# define the service name
	resource = Resource.create({"service.name": "ai-eval-platform"})
	provider = TracerProvider(resource = resource)

	# config OTLP exporter to send traces to jaeger
	try:
		otlp_exporter = OTLPSpanExporter(endpoint = "http://localhost:4317", insecure = True)
		provider.add_span_processor(BatchSpanProcessor(otlp_exporter))
		logger.info("OpenTelemetry configured. Sending traces to Jaeger.")
	except Exception as e:
		logger.warning(f"Could not connect to Jaeger OTLP endpoint: {e}")

	trace.set_tracer_provider(provider)

	# auto-instrument the stack
	CeleryInstrumentor().instrument() # traces celery tasks
	SQLAlchemyInstrumentor().instrument(engine = engine) # traces postgres queries
	HTTPXClientInstrumentor().instrument() # traces deepseek/telegram api calls

	return trace.get_tracer("eval_platform")