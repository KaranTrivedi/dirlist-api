import configparser
import os
from fastapi import FastAPI

import elastic_calls

from app.root.views import root_router

from app.shows.views import shows_router
from starlette.middleware.cors import CORSMiddleware

import logging

# logging.config.fileConfig('conf/logging.ini')
# log_listener = logging.config.listen(9030)
# log_listener.start()

logger = logging.getLogger(__name__)

origins = [
    "http://localhost:4200",
    "http://192.168.0.16:4200",
]

def add_routes(app: FastAPI):
    app.include_router(root_router)
    app.include_router(shows_router, prefix="/shows")

def create_root_app() -> FastAPI:
    app = FastAPI(
        title="First api",
        description="How does this look",
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