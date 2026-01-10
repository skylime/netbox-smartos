from os import environ

# Set LOGLEVEL in netbox.env or docker-compose.overide.yml to override a logging level of INFO.
LOGLEVEL = environ.get("LOGLEVEL", "DEBUG")

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "DEBUG",
    },
    "loggers": {
        "asyncio": {
            "level": "WARNING",
        },
    },
}
