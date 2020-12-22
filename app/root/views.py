#!./venv/bin/python

"""
Root folder.
"""

import logging
from pathlib import Path

from fastapi import APIRouter

root_router = APIRouter()

logger = logging.getLogger(__name__)

@root_router.get("/health")
def health():
    return {"heathy" : True}

@root_router.get("/test")
def test():
    logger.info(Path(__file__).parent.absolute())
    try:
        (Path("data") / "downloads"/ "test.txt").touch()
    except Exception as exp:
        logger.exception(exp)
        return str(exp)
