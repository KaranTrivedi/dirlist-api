#!./venv/bin/python

"""
Api for getting files and folders in downloads and archives.
"""

import datetime
import logging
import os
import re
from pathlib import Path
from shutil import copyfile, move

import yt_dlp
from fastapi import APIRouter, HTTPException
from starlette.responses import StreamingResponse

import libs.elastic_calls as elastic_calls
import libs.local_calls as local_calls
import start

# from time import sleep

DATA_PATH = start.CONFIG["global"]["data_path"]
MOVIE_PATH = "media/movies/"

elastic = elastic_calls.elastic_connection()
logger = logging.getLogger(__name__)

directory_router = APIRouter()

TMP_KEYS = []

#FUNCTIONS
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


def read_in_chunks(file_object, chunk_size=1024*1024):
    """
    Lazy function (generator) to read a file piece by piece.
    Default chunk size: 1k.

    Args:
        file_object (File): Pass open file with params 'rb'
        chunk_size (int, optional): [description]. Defaults to 1024.

    Yields:
        [type]: [description]
    """

    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        print(type(data))
        yield data

def get_entities(relative_path, full_path, dirs, query=""):
    """
    Returns list of files and folders for a give path, loading from OS

    Args:
        relative_path ([type]): [description]
        full_path ([type]): [description]
        dirs ([type]): [description]
        query (str, optional): [description]. Defaults to "".

    Returns:
        [type]: [description]
    """

    # listcomp
    files = [
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

    # mtime, or modification time, is when the file was last modified.
    # When you change the contents of a file, its mtime changes.
    # ctime, or change time, is when the file's property changes.
    # It will always be changed when the mtime changes,
    #       but also when you change the file's permissions, name or location.
    # atime, or access time, is updated when the file's contents are read by an application
    # or a command such as grep or cat.

    # Atime can be updated alone
    # Ctime will update atime
    # Mtime will update both atime and ctime.

    # listcomp
    folders = [
        {
            "name": val,
            "modify_time": os.stat(full_path / val).st_ctime * 1000,
            "modify_time_h": datetime.datetime.fromtimestamp(
                int(os.stat(full_path / val).st_ctime)
            ).strftime("%Y-%m-%d %H:%M:%S"),
            "file_count":  len(
                [
                    name for name in os.listdir(full_path / val)
                    if os.path.isfile(os.path.join(full_path / val, name))
                ]
            ),
            "folder_count": len(
                [
                    name for name in os.listdir(full_path / val)
                    if os.path.isdir(os.path.join(full_path / val, name))
                ]
            ),
        }
        for val in dirs
        if os.path.isdir(full_path / val) and query in val.lower()
        ]

    return files, folders

# def download(file_path):
#     """
#     Download file for given path.

#     Args:
#         file_path (string): Path to file.

#     Returns:
#         (StreamingResponse): chunks of data.
#     """

#     headers = {
#     "Accept-Ranges": "bytes",
#     "Content-Length": str(sz),
#     "Content-Range": F"bytes {asked}-{sz-1}/{sz}",
#     }
#     response =  StreamingResponse(streaming_file(file_path, CS, asked), headers=headers)

#     if os.path.isfile(file_path):
#         file_like = open(file_path, mode="rb")
#         return StreamingResponse(file_like)

def yt_dlp_hook(download):
    """
    Youtube download Hook

    Args:
        download (_type_): _description_
    """

    global TMP_KEYS

    if download.keys() != TMP_KEYS:
        logger.info(f'Status: {download["status"]}')
        logger.info(f'Dict Keys: {download.keys()}')
        TMP_KEYS = download.keys()

        # Why not yield data?

        # logger.info(download)
        # logger.info(json.dumps(download, indent=2))

#ROUTES
@directory_router.get("/tree/{relative_path:path}", tags=["directory"])
async def get_tree(relative_path: str):
    """
    Get directory tree for path

    Args:
        relative_path (str): [description]

    Returns:
        [type]: [description]
    """

    results = {}

    relative_path, full_path = set_path(relative_path)

    if os.path.isdir(full_path):
        logger.debug("Path is dir.")
        results["valid"] = True
    else:
        results["valid"] = False
        return results

    try:
        dirs = [item for item in os.listdir(full_path) if os.path.isdir(full_path / item)]
    except Exception as exp:
        logger.exception(exp)
        results["valid"] = False
        return results

    return dirs

@directory_router.get("/folder/{relative_path:path}", tags=["directory"])
async def get_dirs(relative_path: str, sort="asc", column="name", query=""):
    """
    Pass unix like path to endpoint, get list of folders and files as response.\n

    Args:\n
        ui_path (str): unix like path for folder.\n
        sort (str, optional): Sort direction. Defaults to "asc".\n
        column (str, optional): [description]. Defaults to "name".\n

    Returns:\n
        (dict): dict containing a list of folders and files with some metadata
            or file as a response.
    """

    results = {}

    # Get relative (formatted) and full path of given param.
    relative_path, full_path = set_path(relative_path)

    if os.path.isdir(full_path):
        logger.debug("Path is dir.")
        results["valid"] = True
    else:
        results["valid"] = False
        return results

    try:
        dirs = os.listdir(full_path)
    except Exception as exp:
        logger.exception(exp)
        results["valid"] = False
        return results

    # if os.path.isfile(full_path):
    #     logger.info(f"http://{start.IP}:{start.PORT}/path/{relative_path}")
    #     results["valid"] = False
    #     return download(file_path=full_path)

    #Get files and folders.

    results["files"], results["folders"] = get_entities(relative_path, full_path, dirs, query)

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
    # results["path"] = relative_path
    results["file_size_total"] = sum([file["size"] for file in results["files"]])
    results["file_size_total_h"] = local_calls.human_size(results["file_size_total"])

    if "" in results["path_vars"]:
        logger.debug(results["path_vars"])
        results["path_vars"].remove("")

    return results

@directory_router.get("/format_name", tags=["directory"])
def format_file(filename):
    """
    Strips garbage from filenames.

    Args:
        filename (string): Raw file name

    Returns:
        [string]: new filename
    """

    numbers = re.compile(r'([0-9]{4})')
    replace_vals = ["5.1", "-x0r", ".", "_", ",", "AC3", " 720p", " BluRay",\
        " HDRip", " 1080p", " x265", " x264", "Dual", "audio", "FLAC", "10bit", "[",\
        "]", " WEB", " HDR", " Rip", " 10Bit", " H265-d3g", " AMZN-DL", " DDP2", " 264-EVO"]

    file_name = Path(filename)
    name = file_name.stem
    for replace_val in replace_vals:
        if replace_val == ".":
            name = name.replace(replace_val, " ")

        name = name.replace(replace_val, "")

    modified_name = numbers.sub(r'(\1)', name)

    return {
        "full": modified_name + file_name.suffix.lower(),
        "prefix": modified_name,
        "suffix": file_name.suffix.lower()
        }

@directory_router.get("/youtube-dl/{relative_path:path}", tags=["directory"])
async def youtube_dl(relative_path, url, name=""):
    """
    This route accepts URL of a video and its name along with unix relative path,
    and then uses yt_dlp to download file to given location with name.

    Args:
        relative_path (_type_): unix-like path for where file is to be saved.
        url (_type_): url of video to be downloaded
        name (str, optional): Name of file to be saved.

    Returns:
        _type_: _description_
    """

    # youtube-dl --extract-audio --audio-format mp3 --output "%(uploader)s%(title)s.%(ext)s" http://www.youtube.com/watch?v=rtOvBOTyX00

    relative_path, _ = set_path(relative_path)

    logger.info(f"{DATA_PATH}{relative_path}")

    if name:
        name = f"{DATA_PATH}{relative_path}/{name}.%(ext)s"
    else:
        name = f"{DATA_PATH}{relative_path}/%(title)s.%(ext)s"

    def download_progress_hook(progress):
        if progress["status"] == "finished":
            # buffer.close()
            yield 100
        else:
            logger.info(f"{progress['_percent_str']}")
            yield f"{progress['_percent_str']}"

    ydl_opts = {
        "outtmpl": name,
        'format': 'best',
        'progress_hooks': [download_progress_hook]
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:

        return StreamingResponse(ydl.extract_info(url))


@directory_router.get("/youtube-dl-info", tags=["directory"])
def youtube_dl_info(url):
    """
    Show vid info.
    """

    ydl_opts = {}
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        try:
            info = ydl.extract_info(url, download=False)
        except Exception as exp:
            logger.exception(exp)
            return 

    # ℹ️ ydl.sanitize_info makes the info json-serializable
    return ydl.sanitize_info(info)

@directory_router.get("/copy_file/{relative_path:path}", tags=["directory"])
def copy_file(relative_path, filename, destname=""):
    """
    Copy files from give location to Movies folder.

    Args:
        relative_path ([type]): [description]
        filename ([type]): [description]
        destname (str, optional): [description]. Defaults to "".

    Returns:
        [type]: [description]
    """

    # logger.info(filename)
    # logger.info(destname)

    relative_path, full_path = set_path(relative_path)

    if not destname:
        destname = filename

    src = str(full_path) + "/" + filename
    dest = DATA_PATH + MOVIE_PATH + destname

    try:
        copyfile(src, dest) 
        # logger.info(src, dest)
    except Exception as exp:
        logger.exception(exp)
        return str(exp)

    return "Done"

@directory_router.get("/move_file/{relative_path:path}", tags=["directory"])
def move_file(relative_path, filename, destname=""):
    """
    Move files from give location to Movies folder.

    Args:
        relative_path ([type]): [description]
        filename ([type]): [description]
        destname (str, optional): [description]. Defaults to "".

    Returns:
        [type]: [description]
    """

    logger.info(filename)
    logger.info(destname)

    relative_path, full_path = set_path(relative_path)

    if not destname:
        destname = filename

    src = str(full_path) + "/" + filename
    dest = DATA_PATH + MOVIE_PATH + destname

    try:
        logger.info(dest)
        move(src, dest)
    except Exception as exp:
        logger.exception(exp)
        return str(exp)
    return "Done"

@directory_router.get("/file/{relative_path:path}", tags=["directory"])
async def get_file(relative_path):
    """
    Pass full path.

    Args:
        ui_path (str): unix like path for folder.
        sort (str, optional): Sort direction. Defaults to "asc".
        column (str, optional): [description]. Defaults to "name".

    Returns:
        (dict): dict containing a list of folders and files with some metadata
            or file as a response.
    """

    relative_path = relative_path.strip("/")
    logger.debug(f"Loc: {relative_path}")

    try:
        full_path = Path(DATA_PATH) / relative_path
        # logger.info(full_path)
        logger.info(f"http://{start.IP}:{start.PORT}/path/{relative_path}")
    except Exception as exp:
        logger.exception(exp)

    # headers = {
    #     "Accept-Ranges": "bytes",
    #     "Content-Length": str(sz),
    #     "Content-Range": F"bytes {asked}-{sz-1}/{sz}",
    # }
    # response =  StreamingResponse(streaming_file(full_path, CS, asked), headers=headers)

    file_iter = open(full_path, mode="rb")
    return StreamingResponse(read_in_chunks(file_iter))
