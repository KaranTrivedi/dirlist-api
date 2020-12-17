#!./venv/bin/python

"""
Local calls
"""

import base64
import configparser
import sys
import logging
import re
import os
import time

CONFIG = configparser.ConfigParser()
CONFIG.read("conf/config.ini")
SECTION = "local_calls"

logger = logging.getLogger(__name__)

def human_size(num, suffix="B"):
    """
    Convert bytes to human readable format

    Args:
        num (str/float): Send size as string or float.
        suffix (str, optional): Give wanted suffix. Defaults to "B".

    Returns:
        (str): Gives data size in given suffix.
    """

    num = float(num)
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix) 

def main():
    """
    Main function
    """

    logging.basicConfig(
        filename=CONFIG[SECTION]["log"],
        level=CONFIG[SECTION]["level"],
        format="%(asctime)s::%(levelname)s::%(name)s::%(funcName)s::%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    sys.exit()

if __name__ == "__main__":
    main()