#!./venv/bin/python

"""
File to load dirs and files into elastic for search.
"""

from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware

from app.directory.views import directory_router
from app.root.views import root_router
from app.search.views import search_router
from app.metrics.views import metrics_router

# logging.config.fileConfig('conf/logging.conf', disable_existing_loggers=False)

# log_listener = logging.config.listen(9030)
# log_listener.start()

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

app = FastAPI(
    title="Dirslist Api",
    description="API for website",
    version="0.1",
    openapi_tags=tags_metadata
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
