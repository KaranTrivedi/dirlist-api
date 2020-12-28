#!./venv/bin/python

"""
Api for search page
"""

import datetime
import json
import logging
import re
from os import walk
from pathlib import Path

from fastapi import APIRouter

import libs.elastic_calls as elastic_calls
import libs.local_calls as local_calls
import start

search_router = APIRouter()

logger = logging.getLogger(__name__)

elastic = elastic_calls.elastic_connection()
DATA_PATH = start.CONFIG["global"]["data_path"]

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

@search_router.get("/refresh")
def set_search():
    """
    Call to refresh data in elastic.

    Returns:
        (boolean): Returns true once refresh is done.
    """

    logger.info("Starting reload.")
    files = []
    ignored_extensions = [
        "txt",
        "sfv",
        "py",
        "jpg",
        "png",
        "srt",
        "nfo",
        "tbn",
        "ico",
        "ssa",
        "website",
        "old",
        "bat",
        "iso",
        "torrent",
        "db",
        "rar",
        "cue",
        "idk",
        "log",
        "zip",
        "docx",
        "js",
        "rb",
        "md",
        "json",
        "uc",
        "html",
        "xnb",
        "svg",
        "",
    ]
    for (dirpath, _, filenames) in walk(DATA_PATH, followlinks=True):
        for filename in filenames:
            # val = os.path.join(dirpath, filename)
            path = Path(dirpath) / filename
            if (path.suffix[1:].lower() not in ignored_extensions
                    and re.match(r"[0-9]{1,3}", path.suffix[1:]) is None
                ):
                file_dict = {}
                file_dict["index"] = start.CONFIG["dir_loader"]["index"]
                file_dict["name"] = filename
                file_dict["parent"] = str(path.parent)[len(DATA_PATH):] + "/"
                file_dict["path"] = str(path)[len(DATA_PATH):]
                file_dict["url"] = "http://" + start.IP + ":" + start.PORT + "/directory/" + \
                    str(path)[len(DATA_PATH):]
                stats = path.stat()
                file_dict["modify_time"] = stats.st_mtime*1000
                file_dict["modify_time_h"] = datetime.datetime.fromtimestamp(
                    int(stats.st_mtime)
                ).strftime("%Y-%m-%dT%H:%M:%S%z")
                file_dict["size"] = stats.st_size
                file_dict["size_h"] = local_calls.human_size(stats.st_size)
                file_dict["ext"] = path.suffix[1:].lower()

                files.append(file_dict)
                logger.debug(json.dumps(file_dict, indent=2))
                # sys.exit()
        # break

    elastic.indices.delete(index=start.CONFIG["dir_loader"]["index"])
    elastic_calls.elastic_ingest(elastic=elastic, docs=files)

    return True