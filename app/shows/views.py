#!/projects/dirlist/venv/bin/python

'''
Api for getting files and folders
'''

# DEFAULTS
import configparser
# Added
import os
import logging
from logging import getLogger
import pathlib

import start

from fastapi import APIRouter
from starlette.responses import FileResponse, StreamingResponse

shows_router = APIRouter()

# Load config from start file.
SECTION = 'dirlist'
PATH = start.CONFIG[SECTION]["path"]

start.logger = getLogger("shows")
start.logger.setLevel("DEBUG")


@shows_router.get("/folders")
async def get_folders(ui_path=""):
    '''
    Pass path as an array to function.
    Returns folders and files.
    '''

    results = {}

    start.logger.debug("Loc: %s", ui_path)

    entry = pathlib.Path(PATH) / ui_path
    start.logger.debug("Path: %s", entry)

    if os.path.isdir(entry):
        start.logger.debug("Path is dir.")
        results["valid"] = True
    else:
        start.logger.error("Invalid path: %s", entry)
        results["valid"] = False
        return results

    if os.path.isfile(entry):
        start.logger.debug("is file")
        return download(entry)

    dirs = os.listdir(entry)
    # start.logger.debug(dirs)

    results["files"] = [{"name": val} for val in dirs if os.path.isfile(
        entry / val)]
    results["folders"] = [{"name": val}
                          for val in dirs if os.path.isdir(entry / val)]

    # start.logger.debug(results["folders"])

    if ui_path:
        ui_path = str(pathlib.Path(ui_path))

    results["path_vars"] = ui_path.split("/")
    results["path"] = ui_path

    if "" in results["path_vars"]:
        results["path_vars"].remove("")
    start.logger.debug(results["path_vars"])
    return results


def download(file_path):
    '''
    Download file for given path.
    '''
    if os.path.isfile(file_path):
        file_like = open(file_path, mode="rb")
        return StreamingResponse(file_like)
        # return FileResponse(path=file_path)
    return None


@shows_router.get("/file")
async def get_file(ui_path):
    '''
    Pass path to function.
    Returns folders and files.
    '''

    entry = pathlib.Path(PATH) / ui_path
    start.logger.debug("Folder: %s", entry)
    start.logger.debug("Filename: %s", entry.name)

    try:
        if os.path.isfile(entry):
            start.logger.debug("Path valid")
            return download(file_path=entry)
        start.logger.error("Not a file.")
        return "Not a file."
    except Exception as exp:
        start.logger.exception(exp)
        return "Exception has occured"
