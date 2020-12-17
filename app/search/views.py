#!/projects/dirlist/venv/bin/python

"""
Api for getting files and folders
"""

# DEFAULTS
import datetime

# Added
import os
import pathlib
import logging

import elastic_calls

from fastapi import APIRouter
from starlette.responses import StreamingResponse

import start

search_router = APIRouter()
logger = logging.getLogger(__name__)

elastic = elastic_calls.elastic_connection(logger=logger)

@search_router.get("/")
async def get_search(query="*", column="name", sort="asc", size=10, from_doc=0):
    """
    Pass search string to get a list of shows.
    """

    logger.debug(query)

    if column == "name":
        column = "name.keyword"

    _query = {
        "from" : str(from_doc),
        "size" : str(size),
        "sort":
        [
            {
                column: {"order": sort}
            }
        ],
        "query":
        {
            "query_string":
            {
                "query": str(query)
            }
        }
    }

    logger.info(_query)
    files = {}

    try:
        srch = elastic.search(index="files", body=_query)
        files["data"] = [body["_source"] for body in srch["hits"]["hits"]]
        files["length"] = srch["hits"]["total"]["value"]
    except Exception as exp:
        logger.exception(exp)
        files["exception"] = str(exp)

    return files
