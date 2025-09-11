from typing import Dict, Any, override
from datetime import datetime

from strands.telemetry import StrandsTelemetry
from langfuse import Langfuse

from config.app import app_config
from ports.adapters.secondary import O11yAdapter
from utils.logger import logger


class LangfuseO11yAdapter(O11yAdapter):
    def __init__(self):
        self.is_local = app_config.environment == "local"
        self.strands_telemetry = None

        self.langfuse = Langfuse()
        self._setup_telemetry()

    def _setup_telemetry(self):
        try:
            self.strands_telemetry = StrandsTelemetry()

            # Setup OTLP exporter for Langfuse
            self.strands_telemetry.setup_otlp_exporter()

            # Setup console exporter for local debugging
            if self.is_local:
                self.strands_telemetry.setup_console_exporter()

            # Setup meter for metrics collection
            self.strands_telemetry.setup_meter(
                enable_otlp_exporter=True,
                enable_console_exporter=self.is_local,
            )

            logger.info("✅ Observability telemetry setup completed", is_local=self.is_local)

        except Exception as e:
            logger.error(f"🚨 Failed to setup telemetry: {e}", is_local=self.is_local)

    @override
    def create_trace_attributes(
        self,
        agent_name: str,
        **kwargs,
    ) -> Dict[str, Any]:
        return {
            "agent.name": agent_name,
            "environment": "local" if self.is_local else "production",
            "session.timestamp": datetime.now().isoformat(),
            **kwargs,
        }

    def _flush_traces(self):
        try:
            self.langfuse.flush()
            logger.info("✅ Traces flushed successfully")
        except Exception as e:
            logger.warning(f"⚠️ Failed to flush traces: {e}")

    @override
    async def cleanup(self):
        logger.info("🛑 Shutting down observability components...")
        self._flush_traces()
        logger.info("✅ Observability shutdown completed")
