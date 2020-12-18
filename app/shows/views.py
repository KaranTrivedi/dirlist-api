#!./venv/bin/python

"""
Api for getting files and folders in downloads and archives.
"""

# DEFAULTS
import datetime

# Added
import os
import pathlib
import logging

from fastapi import APIRouter
from starlette.responses import StreamingResponse

import libs.elastic_calls as elastic_calls
import libs.local_calls as local_calls

import start

DATA_PATH = start.CONFIG["global"]["data_path"]
logger = logging.getLogger(__name__)
elastic = elastic_calls.elastic_connection()

shows_router = APIRouter()

@shows_router.get("/folders")
async def get_folders(ui_path="", sort="asc", column="name"):
    """
    Pass path as an array to function.
    Returns folders and files.
    """

    results = {}
    ui_path = ui_path.strip("/")
    logger.info(f"Loc: {ui_path}")

    try:
        entry = pathlib.Path(DATA_PATH) / ui_path
    except Exception as exp:
        logger.exception(exp)

    logger.debug("Path: %s", entry)

    if os.path.isdir(entry):
        logger.debug("Path is dir.")
        results["valid"] = True
    else:
        logger.error("Invalid path: %s", entry)
        results["valid"] = False
        return results

    if os.path.isfile(entry):
        results["valid"] = False
        return results

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
            "size_h": local_calls.human_size(os.stat(entry / val).st_size),
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

    entry = pathlib.Path(DATA_PATH) / ui_path
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
