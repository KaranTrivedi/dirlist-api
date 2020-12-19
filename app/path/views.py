#!./venv/bin/python

"""
Api for getting files and folders in downloads and archives.
"""

# DEFAULTS
import datetime
import os
from pathlib import Path
import logging

from fastapi import APIRouter
from starlette.responses import StreamingResponse

import libs.elastic_calls as elastic_calls
import libs.local_calls as local_calls

import start

DATA_PATH = start.CONFIG["global"]["data_path"]
logger = logging.getLogger(__name__)
elastic = elastic_calls.elastic_connection()

path_router = APIRouter()

@path_router.get("/{ui_path:path}")
async def get_path(ui_path: str, sort="asc", column="name"):
    """
    Pass unix like path to endpoint, get list of folders and files as response.

    Args:
        ui_path (str): unix like path for folder.
        sort (str, optional): Sort direction. Defaults to "asc".
        column (str, optional): [description]. Defaults to "name".

    Returns:
        (dict): dict containing a list of folders and files with some metadata
            or file as a response.
    """

    results = {}
    ui_path = ui_path.strip("/")
    logger.debug(f"Loc: {ui_path}")

    try:
        entry = Path(DATA_PATH) / ui_path
    except Exception as exp:
        logger.exception(exp)

    logger.debug(f"Path: {entry}")

    if os.path.isdir(entry):
        logger.debug("Path is dir.")
        results["valid"] = True
    results["valid"] = False

    if os.path.isfile(entry):
        return download(file_path=entry)

    dirs = os.listdir(entry)
    # logger.debug(dirs)

    # listcomp
    results["files"] = [
        {
            "name": val,
            "ext": val[-3:],
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

    # listcomp
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
        ui_path = str(Path(ui_path))

    results["path_vars"] = ui_path.split("/")
    results["path"] = ui_path

    if "" in results["path_vars"]:
        logger.exception(results["path_vars"])
        results["path_vars"].remove("")

    logger.debug(results["path_vars"])

    return results

def download(file_path):
    """
    Download file for given path.

    Args:
        file_path (string): Path to file.

    Returns:
        (StreamingResponse): chunks of data.
    """

    # headers = {
    # "Accept-Ranges": "bytes",
    # "Content-Length": str(sz),
    # "Content-Range": F"bytes {asked}-{sz-1}/{sz}",
    # }
    # response =  StreamingResponse(streaming_file(file_path, CS, asked), headers=headers)

    if os.path.isfile(file_path):
        file_like = open(file_path, mode="rb")
        return StreamingResponse(file_like)
    return None
