#!/projects/dirlist/venv/bin/python

'''
Api for getting files and folders
'''

# DEFAULTS
import configparser
# Added
import os
from logging import getLogger
import pathlib

from fastapi import APIRouter
from starlette.responses import FileResponse

shows_router = APIRouter()

# Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read('/home/karan/projects/dirlist-api/conf/config.ini')
SECTION = 'dirlist'
PATH = CONFIG[SECTION]["path"]
# PATH = app.CONFIG[SECTION]["path"]

logger = getLogger("shows")

@shows_router.get("/folders")
async def get_folders(path=""):
    '''
    Pass path as an array to function.
    Returns folders and files.
    '''

    results = {}

    logger.info("Loc: %s", path)

    if path:
        entry = PATH + "/" + path
        # logger.info(entry)
    else:
        entry = PATH

    if os.path.isdir(entry):
        results["valid"] = True
    else:
        logger.error("Invalid path: %s", entry)
        results["valid"] = False
        return results

    # logger.info("Path: %s", entry)

    if os.path.isfile(entry):
        filename = path.split('/')[-1]
        # logger.info("is file")
        return download(entry, filename)

    dirs = os.listdir(entry)

    results["folders"] = [val for val in dirs if os.path.isdir(entry + "/" + val)]
    results["files"] = [val for val in dirs if os.path.isfile(entry + "/" + val)]

    results["path_vars"] = path.split("/")
    results["path"] = path

    if "" in results["path_vars"]:
        results["path_vars"].remove("")
    return results

def download(path, filename):
    '''
    Download file for given path.
    '''
    if os.path.isfile(path):
        return FileResponse(path=path, filename=filename)
    return None

@shows_router.get("/file")
async def get_file(path):
    '''
    Pass path to function.
    Returns folders and files.
    '''

    entry = PATH + "/" + path
    logger.debug("Folder: %s", entry)
    logger.debug("Filename: %s", entry.split('/')[-1])

    try:
        if os.path.isfile(entry):
            # logger.info("Path valid")
            return download(path=entry, filename=path.split('/')[-1])
        logger.error("Not a file.")
        return "Not a file."
    except Exception as exp:
        logger.exception(exp)
        return "Exception has occured"
