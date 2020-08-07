#!/projects/dirlist/venv/bin/python

'''
Api for getting files and folders
'''

# DEFAULTS
import configparser
# Added
import os
import json
from os import path
from logging import getLogger
import pathlib

from typing import List
from fastapi import APIRouter, Query, Header, HTTPException
# from fastapi.logger import logger as fastapi_logger
# from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

shows_router = APIRouter()

# Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read('/home/karan/projects/dirlist-api/conf/config.ini')
SECTION = 'dirlist'
PATH = CONFIG[SECTION]["path"]
# PATH = app.CONFIG[SECTION]["path"]

logger = getLogger("dirlist")

# app.mount("/files", StaticFiles(directory="/shows"), name="shows")

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
        logger.info(entry)
    else:
        entry = PATH
    
    logger.info("Path: %s", entry)

    if os.path.isfile(entry):
        filename = path.split('/')[-1]
        logger.info("is file")
        return download(entry, filename)

    dirs = os.listdir(entry)
    results["folders"] = [
        val for val in dirs if os.path.isdir(entry + "/" + val)]
    results["files"] = [val for val in dirs if os.path.isfile(entry + "/" + val)]
    
    results["path_vars"] = path.split("/")
    results["path"] = path

    if "" in results["path_vars"]:
        results["path_vars"].remove("")
    return results

def download(path, filename):
    if os.path.isfile(path):
        return FileResponse(path=path, media_type="application/octet-stream",filename=filename)

@shows_router.get("/file")
async def get_file(path):
    '''
    Pass path to function.
    Returns folders and files.
    '''

    entry = PATH + path
    logger.info("Folder: %s", entry)
    logger.info("Filename: %s", entry.split('/')[-1])
    try:
        if os.path.isfile(entry):
            logger.info("Path valid")
            return FileResponse(path=entry, filename=path.split('/')[-1], media_type='application/octet-stream')
        else:
            return "Not a file."
    except Exception as exp:
        logger.exception(exp)
        return "Exception has occured"
