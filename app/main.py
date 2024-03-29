#!./venv/bin/python

"""
File to load dirs and files into elastic for search.
"""

from fastapi import FastAPI, WebSocket
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

import logging

import asyncio


from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.directory.views import directory_router
from app.root.views import root_router
from app.search.views import search_router
from app.metrics.views import metrics_router
from app.mailer.views import mailer_router
from app.download.views import download_router

from asgi_logger import AccessLoggerMiddleware
from starlette.middleware import Middleware

logger = logging.getLogger(__name__)

origins = [
    "http://localhost:4200",
    "http://192.168.0.16:4200",
    "http://192.168.0.16:4201"
]

tags_metadata = [
    {
        "name": "root",
        "description": "Root router",
    },
    {
        "name": "search",
        "description": "Search related functions",
        "externalDocs": {
            "description": "Items external docs",
            "url": "http://192.168.0.16:4200/search",
        },
    },
    {
        "name": "directory",
        "description": "Unix Path related functions.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "http://192.168.0.16:4200/directory",
        },
    },
    {
        "name": "metrics",
        "description": "Metrics related functions.",
        "externalDocs": {
            "description": "Items external docs",
            "url": "http://192.168.0.16:4200/metrics",
        },
    },
]

app = FastAPI(
        title="Dirslist Api",\
        openapi_tags=tags_metadata,\
        description="API for Dirlist Site",\
        version="0.1",
        # middleware=[Middleware(AccessLoggerMiddleware)]
    )

app.connections = []

# AccessLoggerMiddleware(app, format='%(client_addr)s - "%(request_line)s" %(L)s %(B)s %(status_code)s')

app.mount("/swagger-ui", StaticFiles(directory="swagger-ui"), name="swagger-ui")

@app.get("/docs/dark", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Trying to load in custom CSS file for docs pages.

    Returns:
        [type]: [description]
    """

    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title = f"{app.title} - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        # swagger_js_url="https://cdn.jsdelivr.net/npm/swagger-ui-dist@3/swagger-ui-bundle.js",
        swagger_css_url="/swagger-ui/swagger-ui.css"
    )

app.mount("/directory1/downloads", StaticFiles(directory="directory/downloads"), name="directory1/downloads")
# app.mount("/directory1/documents", StaticFiles(directory="directory/documents"), name="directory1/documents")
# app.mount("/directory1/archives", StaticFiles(directory="directory/downloads"), name="directory1/archives")
app.mount("/directory1/media", StaticFiles(directory="directory/media"), name="directory1/media")
app.mount("/directory1", StaticFiles(directory="directory"), name="directory1")

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    """
    Trying to load in custom CSS file for docs pages.

    Returns:
        [type]: [description]
    """
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc_dark", include_in_schema=False)
async def redoc_html():
    """
    Trying to load in custom CSS file for docs pages.

    Returns:
        [type]: [description]
    """
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )

app.include_router(root_router)
app.include_router(directory_router, prefix="/directory")
app.include_router(search_router, prefix="/search")
app.include_router(metrics_router, prefix="/metrics")
app.include_router(mailer_router, prefix="/mailer")
app.include_router(download_router, prefix="/download")

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    AccessLoggerMiddleware,
    format='%(client_addr)s - "%(request_line)s" %(L)s %(B)s %(status_code)s',
    logger=logging.getLogger("asgi-logger")
)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    ??

    Args:
        websocket (WebSocket): _description_
    """
    await websocket.accept()
    app.connections.append(websocket)
