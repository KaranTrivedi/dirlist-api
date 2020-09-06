from fastapi import APIRouter
from urllib.parse import unquote
from logging import getLogger
import subprocess

root_router = APIRouter()

# logger = getLogger("views")

@root_router.get("/health")
def health():
    return {"heathy" : True}

@root_router.get("/path/{path:path}")
def take_path(path: str):
    # logger.info( f"Path: {path}")
    return path

@root_router.get("/search")
def get_search(find):
    search = subprocess.Popen(["find", "/mnt", "-name", find], stderr=subprocess.PIPE)
    output = search.stderr.read()

    return output
