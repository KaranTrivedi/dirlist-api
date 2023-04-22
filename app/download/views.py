#!./venv/bin/python

"""
Api for getting files and folders in downloads and archives.
"""

import logging
from pathlib import Path

import yt_dlp
from fastapi import APIRouter, HTTPException

from fastapi import Request, Response
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import libs.elastic_calls as elastic_calls
import start
import app

DATA_PATH = start.CONFIG["global"]["data_path"]
MOVIE_PATH = "media/movies/"

elastic = elastic_calls.elastic_connection()
logger = logging.getLogger(__name__)

download_router = APIRouter()

class DownloadRequest(BaseModel):
    url: str
    name: str

def set_path(relative_path):
    """
    Create and format relative and full paths from given

    Args:
        relative_path ([type]): [description]

    Returns:
        [type]: [description]
    """

    relative_path = relative_path.strip("/")
    logger.debug(f"Loc: {relative_path}")

    try:
        full_path = Path(DATA_PATH) / relative_path
    except Exception as exp:
        logger.exception(exp)

    logger.debug(f"Path: {full_path}")

    return relative_path, full_path

@download_router.post("/youtube-dl/{relative_path:path}", tags=["download"])
async def download_video(relative_path, download_request: DownloadRequest):
    """
    download file from url func.

    Args:
        relative_path (_type_): _description_
        request (Request): _description_
        download_request (DownloadRequest): _description_

    Returns:
        _type_: _description_
    """

    relative_path, _ = set_path(relative_path)

    logger.info(f"{DATA_PATH}{relative_path}")

    progress = {"progress": 0}

    if download_request.name:
        name = f"{DATA_PATH}{relative_path}/{download_request.name}.%(ext)s"
    else:
        name = f"{DATA_PATH}{relative_path}/%(title)s.%(ext)s"

    ydl_opts = {
        'outtmpl': name,
        "quiet": True,
        'format': 'best',
        'logger': logger,
        'progress_hooks': [lambda d: progress_callback(d, progress)],
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([download_request.url])
    return {"status": "success", "progress": progress["progress"]}

def progress_callback(d, progress):
    if d["status"] == "downloading":
        progress["progress"] = int(d["_percent_str"].strip("%").split(".")[0])
        logger.info(progress["progress"])
        websocket_send(app)

async def websocket_send(app):
    """
    

    Args:
        app (_type_): _description_
    """

    logger.info("Did this trigger?")

    for connection in app.connections:
        try:
            await connection.send_json({"progress": app.progress})
        except:
            app.connections.remove(connection)