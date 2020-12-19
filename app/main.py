#!./venv/bin/python

import configparser
import os
from fastapi import FastAPI
import start

from app.root.views import root_router
from app.path.views import path_router
from app.search.views import search_router

from starlette.middleware.cors import CORSMiddleware

import logging

# SECTION = "main"

# CONFIG = configparser.ConfigParser()
# CONFIG.read("conf/config.ini")

# logging.config.fileConfig('conf/logging.conf', disable_existing_loggers=False)

# log_listener = logging.config.listen(9030)
# log_listener.start()

logger = logging.getLogger(__name__)

origins = [
    "http://localhost:4200",
    "http://192.168.0.16:4200"
]

app = FastAPI(
    title="First api",
    description="API for website",
    version="0.1"
)
app.include_router(root_router)
app.include_router(path_router, prefix="/path")
app.include_router(search_router, prefix="/search")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ != '__main__':
    uvicorn_logger = logging.getLogger('uvicorn')
    print(logging.getLogger('uvicorn').handlers)
    print(logging.getLogger('uvicorn.error').handlers)
    print(logging.getLogger('uvicorn.access').handlers)
    print(logger.handlers)
    print(logger.name)

    # logger.handlers = uvicorn_logger.handlers
    # logger.setLevel(uvicorn_logger.level)

# @app.on_event("startup")
# async def startup_event():
#     logging.config.fileConfig('conf/logging.conf', disable_existing_loggers=True)
