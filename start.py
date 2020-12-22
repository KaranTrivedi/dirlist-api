#!./venv/bin/python

"""
Start file for initiating uvicorn.
"""

import configparser
import logging

import uvicorn

# Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read('conf/config.ini')
SECTION = "start"
IP = "192.168.0.16"
PORT = 8000

logging.basicConfig(
    filename=CONFIG[SECTION]["default"],
    level=CONFIG[SECTION]["level"],
    format="%(asctime)s::%(levelname)s::%(name)s::%(funcName)s::%(message)s",
    datefmt="%Y-%m-%dT%H:%M:%S%z",
)

# ./venv/lib/python3.8/site-packages/uvicorn/config.py
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "()": "uvicorn.logging.DefaultFormatter",
            "fmt": "%(asctime)s::%(levelname)s::%(name)s::%(filename)s::%(funcName)s::%(message)s",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            "use_colors": False,
        },
        "access": {
            "()": "uvicorn.logging.AccessFormatter",
            "datefmt": "%Y-%m-%dT%H:%M:%S%z",
            "fmt": '%(asctime)s::%(levelprefix)s %(client_addr)s - "%(request_line)s" %(msecs)d %(status_code)s',
            "use_colors": False,
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
        "uvicorn": {"handlers": ["default"], "level": "INFO", "propagate": False},
        "uvicorn.error": {"handlers": ["error"], "level": "INFO", "propagate": False},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    }
}

if __name__ == "__main__":

    uvicorn.run(
        app="app.main:app",
        host=IP,
        port=PORT,
        reload=True,
        log_config=log_config,
        log_level="info"
    )
