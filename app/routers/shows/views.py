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

from typing import List
from fastapi import APIRouter, Query, Header, HTTPException
# from fastapi.logger import logger as fastapi_logger
# from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse

shows_router = APIRouter()

# Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read('/projects/dirlist/conf/config.ini')
SECTION = 'dirlist'
PATH = CONFIG[SECTION]["path"]

logger = getLogger("dirlist")

# app.mount("/files", StaticFiles(directory="/shows"), name="shows")

@shows_router.get("/")
async def get_shows(q: List[str] = Query(None)):
    '''
    Pass path as an array to function.
    Returns folders and files.
    '''

    results = {}

    logger.info("test")

    filename = q[-1]

    query_items = {"q": q}
    if query_items["q"]:
        entry = PATH + "/".join(query_items["q"])
    else:
        entry = PATH

    if os.path.isfile(entry):
        return download(entry, filename)

    dirs = os.listdir(entry + "/")
    results["folders"] = [
        val for val in dirs if os.path.isdir(entry + "/"+val)]
    results["files"] = [val for val in dirs if os.path.isfile(entry + "/"+val)]
    results["path_vars"] = query_items["q"]

    return results

def download(path, filename):
    if os.path.isfile(path):
        return FileResponse(path=path, media_type="application/octet-stream",filename=filename)

@shows_router.get("/file")
async def get_file(q: List[str] = Query(None)):
    '''
    Pass path to function.
    Returns folders and files.
    '''

    query_items = {"q": q}
    if query_items["q"]:
        entry = PATH + "/".join(query_items["q"])
    else:
        entry = PATH
    try:
        if os.path.isfile(entry):
            return FileResponse(path=entry, filename=query_items["q"][-1])
        else:
            return "Not a file."
    except:
        return "Not a path."

# def main():
#     '''
#     Main function.
#     '''
#     uvicorn.run("dirlist:app", host="0.0.0.0", port=8000, reload=True)

# if __name__ == '__main__':
#     main()
