import configparser
import logging
import os
from fastapi import FastAPI

from app.routers.views import root_router
from app.routers.shows.views import shows_router
from starlette.middleware.cors import CORSMiddleware

origins = [
    "http://localhost:4200",
    "http://192.168.0.16:4200",
]

# Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read('/home/karan/projects/dirlist-api/conf/config.ini')
SECTION = 'dirlist'
PATH = CONFIG[SECTION]["path"]

logger = logging.getLogger("root")

def add_routes(app: FastAPI):
    logger.info("Mounting routes")
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
