#!./venv/bin/python

import configparser
import os
from fastapi import FastAPI
import start

from app.root.views import root_router
from app.shows.views import shows_router
from app.search.views import search_router

from starlette.middleware.cors import CORSMiddleware

import logging

SECTION = "app"

logger = logging.getLogger(__name__)

logging.config.fileConfig('conf/logging.conf', disable_existing_loggers=False)

# logging.config.fileConfig('conf/logging.ini')
# # log_listener = logging.config.listen(9030)
# # log_listener.start()

# logger = logging.getLogger("root")
# logger.info("test")

# CONFIG = configparser.ConfigParser()
# CONFIG.read("conf/config.ini")

# logging.config.fileConfig('conf/logging.ini')
# log_listener = logging.config.listen(9030)
# log_listener.start()

origins = [
    "http://localhost:4200",
    "http://192.168.0.16:4200"
]

def add_routes(app: FastAPI):
    app.include_router(root_router)
    app.include_router(shows_router, prefix="/shows")
    app.include_router(search_router, prefix="/search")

def create_root_app() -> FastAPI:

    app = FastAPI(
        title="First api",
        description="API for website",
        version="0.1"
    )
    add_routes(app)

    app.add_middleware(
        CORSMiddleware,
        allow_origins=origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    return app

app = create_root_app()
