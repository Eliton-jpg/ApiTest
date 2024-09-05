from opentelemetry import trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

def setup_tracing(app):
    # Configuração do Jaeger Exporter
    jaeger_exporter = JaegerExporter(
        agent_host_name="localhost",  # Endereço do Jaeger
        agent_port=6831,  # Porta do agente do Jaeger
    )

    # Configuração do TracerProvider
    trace.set_tracer_provider(
        TracerProvider(
            resource=Resource.create({SERVICE_NAME: "my-fastapi-app"})
        )
    )

    tracer_provider = trace.get_tracer_provider()
    tracer_provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

    # Instrumentando a aplicação FastAPI
    FastAPIInstrumentor.instrument_app(app)
