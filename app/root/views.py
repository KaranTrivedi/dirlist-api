from fastapi import APIRouter
from urllib.parse import unquote
import subprocess
import logging

root_router = APIRouter()

# logger = getLogger("views")
logger = logging.getLogger(__name__)

@root_router.get("/health")
def health():
    return {"heathy" : True}

@root_router.get("/path/{path:path}")
def take_path(path: str):
    # logger.info( f"Path: {path}")
    return path
