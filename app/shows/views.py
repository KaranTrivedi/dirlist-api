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

from fastapi import APIRouter
from starlette.responses import StreamingResponse

import app
import start

shows_router = APIRouter()

# Load config from start file.
SECTION = "dirlist"
PATH = start.CONFIG[SECTION]["path"]

# logger = app.root.views.startup_event()

logger = logging.getLogger(__name__)

elastic = app.elastic_calls.elastic_connection(logger=logger)

def human_size(num, suffix="B"):
    """
    Convert bytes to human readable format
    """
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)

@shows_router.get("/folders")
async def get_folders(ui_path="", sort="asc", column="name"):
    """
    Pass path as an array to function.
    Returns folders and files.
    """

    results = {}
    ui_path = ui_path.strip("/")
    logger.debug("Loc: %s", ui_path)

    try:
        entry = pathlib.Path(PATH) / ui_path
    except Exception as exp:
        logger.exception(exp)

    logger.debug("Path: %s", entry)

    if os.path.isdir(entry):
        logger.debug("Path is dir.")
        results["valid"] = True
    else:
        logger.error("Invalid path: %s", entry)
        results["valid"] = False
        results["valid"] = False
        return results

    if os.path.isfile(entry):
        logger.debug("is file")
        return download(entry)

    dirs = os.listdir(entry)
    # logger.debug(dirs)

    results["files"] = [
        {
            "name": val,
            "modify_time": os.stat(entry / val).st_ctime,
            "modify_time_h": datetime.datetime.fromtimestamp(
                int(os.stat(entry / val).st_ctime)
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "size": os.stat(entry / val).st_size,
            "size_h": human_size(os.stat(entry / val).st_size),
        }
        for val in dirs
        if os.path.isfile(entry / val)
    ]
    # logger.debug(results["files"])
    results["folders"] = [
        {
            "name": val,
            "modify_time": os.stat(entry / val).st_ctime,
            "modify_time_h": datetime.datetime.fromtimestamp(
                int(os.stat(entry / val).st_ctime)
            ).strftime("%Y-%m-%d %H:%M:%S"),
        }
        for val in dirs
        if os.path.isdir(entry / val)
    ]

    # logger.debug(results["folders"])

    if column == "name":
        if sort == "asc":
            results["files"] = sorted(
                results["files"], key=lambda k: k["name"].casefold())
            results["folders"] = sorted(
                results["folders"], key=lambda k: k["name"].casefold())
        else:
            results["files"] = sorted(
                results["files"], key=lambda k: k["name"].casefold(), reverse=True
            )
            results["folders"] = sorted(
                results["folders"], key=lambda k: k["name"].casefold(), reverse=True
            )

    elif column == "modify_time":
        if sort == "asc":
            results["files"] = sorted(
                results["files"], key=lambda k: k["modify_time"])
            results["folders"] = sorted(
                results["folders"], key=lambda k: k["modify_time"])
        else:
            results["files"] = sorted(
                results["files"], key=lambda k: k["modify_time"], reverse=True
            )
            results["folders"] = sorted(
                results["folders"], key=lambda k: k["modify_time"], reverse=True
            )

    elif column == "size":
        # Sort folder by name, files by size.
        if sort == "asc":
            results["files"] = sorted(
                results["files"], key=lambda k: k["size"])
            results["folders"] = sorted(
                results["folders"], key=lambda k: k["name"].casefold())
        else:
            results["files"] = sorted(
                results["files"], key=lambda k: k["size"], reverse=True
            )
            results["folders"] = sorted(
                results["folders"], key=lambda k: k["name"].casefold(), reverse=True
            )

    if ui_path:
        ui_path = str(pathlib.Path(ui_path))

    results["path_vars"] = ui_path.split("/")
    results["path"] = ui_path

    if "" in results["path_vars"]:
        results["path_vars"].remove("")

    logger.debug(results["path_vars"])
    return results


def download(file_path):
    """
    Download file for given path.

    Args:
        file_path ([type]): [description]

    Returns:
        [type]: [description]
    """
    if os.path.isfile(file_path):
        file_like = open(file_path, mode="rb")
        return StreamingResponse(file_like, media_type="video/mp4")
    return None


@shows_router.get("/file")
async def get_file(ui_path):
    """
    Pass path to function.
    Returns folders and files.
    """

    entry = pathlib.Path(PATH) / ui_path
    logger.debug("Folder: %s", entry)
    logger.debug("Filename: %s", entry.name)

    try:
        if os.path.isfile(entry):
            logger.debug("Path valid")
            return download(file_path=entry)
        logger.error("Not a file.")
        return "Not a file."
    except Exception as exp:
        logger.exception(exp)
        return "Exception has occured"

@shows_router.get("/search")
async def get_search(search="*", column="name", sort="asc", size=10, from_doc=0):
    """
    Pass search string to get a list of shows.
    """

    logger.debug(search)

    if column == "name":
        column = "name.keyword"

    query = {
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
                "query": search
            }
        }
    }

    files = {}

    try:
        srch = elastic.search(index="files", body=query)
        files["data"] = [body["_source"] for body in srch["hits"]["hits"]]
        files["length"] = srch["hits"]["total"]["value"]
    except Exception as exp:
        logger.exception(exp)
        files["exception"] = str(exp)

    return files

@shows_router.post("/failed_shows")
async def failed_shows(show):
    """
    Catch list of shows
    Args:
        ui_path (str, optional): [description]. Defaults to "".
        sort (str, optional): [description]. Defaults to "asc".
        column (str, optional): [description]. Defaults to "name".
    """

    logger.info(show)

    return show
