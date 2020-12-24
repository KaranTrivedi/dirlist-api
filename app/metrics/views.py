#!./venv/bin/python

"""
Api for metrics page
"""

import logging
import subprocess
from fastapi import APIRouter

metrics_router = APIRouter()

logger = logging.getLogger(__name__)

@metrics_router.get("/temp")
async def temp():
    """
    Return sensor temps

    Returns:
        [type]: [description]
    """
    ff_command = ["sensors", "-u"]

    output, error = subprocess.Popen(
        ff_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
    ).communicate()

    if not error:
        return output.decode().strip()

    logger.error(error.decode().replace("\n", " "))
    return {}
