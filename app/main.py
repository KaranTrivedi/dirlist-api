#!./venv/bin/python

"""
File to load dirs and files into elastic for search.
"""

from fastapi import FastAPI
from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from fastapi.staticfiles import StaticFiles
from starlette.middleware.cors import CORSMiddleware

from app.directory.views import directory_router
from app.root.views import root_router
from app.search.views import search_router
from app.metrics.views import metrics_router

from asgi_logger import AccessLoggerMiddleware
from starlette.middleware import Middleware

# logging.config.fileConfig('conf/logging.conf', disable_existing_loggers=False)
# logging.config.fileConfig('conf/logging.ini', disable_existing_loggers=True)

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

app = FastAPI(title="Dirslist Api",\
        openapi_tags=tags_metadata,\
        description="API for Dirlist Site",\
        version="0.1",\
        middleware=[Middleware(AccessLoggerMiddleware)])

app.mount("/directory1/downloads", StaticFiles(directory="directory/downloads"), name="directory1/downloads")
# app.mount("/directory1/documents", StaticFiles(directory="directory/documents"), name="directory1/documents")
# app.mount("/directory1/archives", StaticFiles(directory="directory/downloads"), name="directory1/archives")
app.mount("/directory1/media", StaticFiles(directory="directory/media"), name="directory1/media")
app.mount("/directory1", StaticFiles(directory="directory"), name="directory1")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    """
    Trying to load in custom CSS file for docs pages.

    Returns:
        [type]: [description]
    """

    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    """
    Trying to load in custom CSS file for docs pages.

    Returns:
        [type]: [description]
    """
    return get_swagger_ui_oauth2_redirect_html()


@app.get("/redoc", include_in_schema=False)
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

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.on_event("startup")
# async def startup_event():
#     logging.config.fileConfig('conf/logging.ini', disable_existing_loggers=True)

    # logging.basicConfig(
    #     filename=start.CONFIG[start.SECTION]["default"],
    #     level=start.CONFIG[start.SECTION]["level"],
    #     format="%(asctime)s::%(levelname)s::%(name)s::%(funcName)s::%(message)s",
    #     datefmt="%Y-%m-%dT%H:%M:%S%z",
    # )

# if __name__ != '__main__':
    # logger = logging.getLogger('uvicorn')
    # print(logger.name)
    # print(logger.handlers)
