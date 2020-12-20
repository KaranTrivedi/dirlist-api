#!/projects/dirlist/venv/bin/python

"""
Api for search page
"""

import logging

from fastapi import APIRouter

import libs.elastic_calls as elastic_calls

search_router = APIRouter()

logger = logging.getLogger(__name__)

elastic = elastic_calls.elastic_connection()

@search_router.get("/")
async def get_search(query="*", column="name", sort="asc", size=10, from_doc=0):
    """
    Pass search string to get a list of shows.

    Args:
        query (str, optional): [description]. Defaults to "*".
        column (str, optional): [description]. Defaults to "name".
        sort (str, optional): [description]. Defaults to "asc".
        size (int, optional): [description]. Defaults to 10.
        from_doc (int, optional): [description]. Defaults to 0.

    Returns:
        [type]: Files found
    """

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

    logger.debug(_query)

    files = {}

    try:
        srch = elastic.search(index="files", body=_query)
        files["data"] = [body["_source"] for body in srch["hits"]["hits"]]
        files["length"] = srch["hits"]["total"]["value"]
    except Exception as exp:
        logger.exception(exp)
        files["exception"] = str(exp)

    return files
