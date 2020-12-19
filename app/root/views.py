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
