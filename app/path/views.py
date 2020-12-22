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

@path_router.get("/{relative_path:path}")
async def get_path(relative_path: str, sort="asc", column="name", query=""):
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
    relative_path = relative_path.strip("/")
    logger.debug(f"Loc: {relative_path}")

    try:
        full_path = Path(DATA_PATH) / relative_path
    except Exception as exp:
        logger.exception(exp)

    logger.debug(f"Path: {full_path}")

    if os.path.isdir(full_path):
        logger.debug("Path is dir.")
        results["valid"] = True
    else:
        results["valid"] = False

    if os.path.isfile(full_path):
        logger.info(f"http://{start.IP}:{start.PORT}/path/{relative_path}")
        return download(file_path=full_path)

    try:
        dirs = os.listdir(full_path)
    except Exception as exp:
        logger.exception(exp)
        results["valid"] = False
        return results

    # listcomp
    results["files"] = [
        {
            "name": val,
            "ext": Path(full_path / val).suffix[1:].lower(),
            "modify_time": os.stat(full_path / val).st_ctime * 1000,
            "modify_time_h": datetime.datetime.fromtimestamp(
                int(os.stat(full_path / val).st_ctime)
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "size": os.stat(full_path / val).st_size,
            "size_h": local_calls.human_size(os.stat(full_path / val).st_size),
            "path": Path(relative_path),
        }
        for val in dirs
        # Make sure path is file and name contains query chars
        if os.path.isfile(full_path / val) and query in val.lower()
    ]

    # listcomp
    results["folders"] = [
        {
            "name": val,
            "modify_time": os.stat(full_path / val).st_ctime * 1000,
            "modify_time_h": datetime.datetime.fromtimestamp(
                int(os.stat(full_path / val).st_ctime)
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "file_count":  len([name for name in os.listdir(full_path / val) if os.path.isfile(os.path.join(full_path / val, name))]),
            "folder_count":  len([name for name in os.listdir(full_path / val) if os.path.isdir(os.path.join(full_path / val, name))]),
        }
        for val in dirs
        if os.path.isdir(full_path / val) and query in val.lower()
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
        if sort == "asc":
            results["files"] = sorted(
                results["files"], key=lambda k: k["size"])
        else:
            results["files"] = sorted(
                results["files"], key=lambda k: k["size"], reverse=True)

    if relative_path:
        relative_path = str(Path(relative_path))

    results["path_vars"] = relative_path.split("/")
    results["path"] = relative_path

    if "" in results["path_vars"]:
        logger.debug(results["path_vars"])
        results["path_vars"].remove("")

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
