import structlog
import logging
import sys
from typing import Any, Dict


def setup_logging(
    log_level: str = "INFO",
    json_logs: bool = False,
    service_name: str = "cms-nbi-client"
) -> None:
    """Configure structured logging for the application"""
    
    # Configure stdlib logging
    logging.basicConfig(
        format="%(message)s",
        stream=sys.stdout,
        level=getattr(logging, log_level.upper())
    )
    
    # Configure structlog
    processors = [
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.CallsiteParameterAdder(
            parameters=[
                structlog.processors.CallsiteParameter.FILENAME,
                structlog.processors.CallsiteParameter.LINENO,
                structlog.processors.CallsiteParameter.FUNC_NAME
            ]
        ),
    ]
    
    # Add service name to all logs
    processors.append(
        structlog.processors.add_log_level_number
    )
    processors.append(
        lambda _, __, event_dict: {
            **event_dict,
            "service": service_name
        }
    )
    
    # Choose renderer based on json_logs flag
    if json_logs:
        processors.append(structlog.processors.JSONRenderer())
    else:
        processors.append(structlog.dev.ConsoleRenderer(
            colors=True,
            exception_formatter=structlog.dev.better_traceback
        ))
    
    structlog.configure(
        processors=processors,
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str = None) -> structlog.BoundLogger:
    """Get a configured logger instance"""
    return structlog.get_logger(name)


class LogContext:
    """Context manager for adding temporary log context"""
    
    def __init__(self, logger: structlog.BoundLogger, **kwargs):
        self.logger = logger
        self.context = kwargs
        self.token = None
        
    def __enter__(self):
        self.token = structlog.contextvars.bind_contextvars(**self.context)
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.token:
            structlog.contextvars.unbind_contextvars(*self.context.keys())