#!./venv/bin/python

import uvicorn
import configparser
import logging
import json

# Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read('conf/config.ini')
SECTION = "start"

logger = logging.getLogger(__name__)

# ./venv/lib/python3.8/site-packages/uvicorn/config.py
log_config = {
    "version": 1,
    "disable_existing_loggers": True,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s::%(levelname)s::%(name)s::%(filename)s::%(funcName)s - %(message)s",
            "use_colors": None,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "fmt": '%(levelprefix)s %(client_addr)s - "%(request_line)s" %(status_code)s',
        },
    },
    "handlers":
    {
        "default":
        {
            "formatter": "default",
            # "class": 'logging.NullHandler',
            "class": 'logging.FileHandler',
            "filename": CONFIG[SECTION]["default"]
        },
        "error":
        {
            "formatter": "default",
            # "class": 'logging.NullHandler',
            "class": 'logging.FileHandler',
            "filename": CONFIG[SECTION]["error"]
        },
        "access":
        {
            "formatter": "access",
            # "class": 'logging.NullHandler',
            "class": 'logging.FileHandler',
            "filename": CONFIG[SECTION]["access"]
        },
    },
    "loggers":
    {
        "uvicorn": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "ERROR"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    }
}

# log_config = {}

if __name__ == "__main__":

    # logging.basicConfig(
    #     filename=CONFIG[SECTION]["log"],
    #     level=CONFIG[SECTION]["level"],
    #     format="%(asctime)s::%(levelname)s::%(name)s::%(funcName)s::%(message)s",
    #     datefmt="%Y-%m-%d %H:%M:%S",
    # )

    # logging.config.fileConfig('conf/logging.conf', disable_existing_loggers=False)

    uvicorn.run(
        app="app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=log_config,
        log_level="info"
    )
