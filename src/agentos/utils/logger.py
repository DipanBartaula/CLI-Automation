import structlog
from pathlib import Path
from config.settings import settings

def setup_logging():
    """Configure structured logging."""
    # Create log directory
    settings.log_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.dev.ConsoleRenderer() if settings.log_level == "DEBUG" 
            else structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            getattr(structlog.stdlib, settings.log_level)
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(
            file=open(settings.log_path, "a")
        ),
        cache_logger_on_first_use=False,
    )
