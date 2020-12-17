#!./venv/bin/python

import uvicorn
import configparser
import logging
import json

# Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read('conf/config.ini')

# ./venv/lib/python3.8/site-packages/uvicorn/config.py
log_config = {
    "version": 1,
    "disable_existing_loggers": False,
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
    "handlers": {
        "default": {
            "formatter": "default",
            "class": 'logging.FileHandler',
            "filename": "logs/default.log"
        },
        "access": {
            "formatter": "access",
            "class": 'logging.FileHandler',
            "filename": "logs/access.log"
        },
    },
    "loggers": {
        "uvicorn": {"handlers": ["default"], "level": "INFO"},
        "uvicorn.error": {"level": "INFO"},
        "uvicorn.access": {"handlers": ["access"], "level": "INFO", "propagate": False},
    },
}

# log_config["formatters"]["access"]["fmt"] = "%(asctime)s - %(levelname)s - %(message)s"
# log_config["formatters"]["default"]["fmt"] = "%(asctime)s::%(levelname)s::%(name)s::%(filename)s::%(funcName)s - %(message)s"

if __name__ == "__main__":
    uvicorn.run(app="app.main:app", host="0.0.0.0",
                port=8000, reload=True, log_config=log_config, log_level="debug")
