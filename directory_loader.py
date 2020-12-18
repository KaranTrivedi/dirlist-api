#!./venv/bin/python
"""
Read dirs and folders into elasticsearch.
"""

# DEFAULTS
import configparser
import datetime
import json
import logging
import os
import pathlib
import re
from os import walk
from os.path import isfile, join

os.chdir("/home/karan/projects/dirlist-api")

import libs.elastic_calls as elastic_calls
# from .. libs import elastic_calls

# Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read("conf/config.ini")
SECTION = "dir_loader"
logger = logging.getLogger(SECTION)


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
    Main function.
    """

    logging.basicConfig(
        filename=CONFIG[SECTION]["log"],
        level=CONFIG[SECTION]["level"],
        format="%(asctime)s::%(levelname)s::%(name)s::%(funcName)s::%(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logger.info("####################STARTING####################")

    internal = "G:\\4. Videos"
    data_dir = "data"
    files = []
    ignored_extensions = [
        "txt",
        "sfv",
        "py",
        "jpg",
        "png",
        "srt",
        "nfo",
        "tbn",
        "ico",
        "ssa",
        "website",
        "old",
        "bat",
        "iso",
        "torrent",
        "db",
        "rar",
        "cue",
        "idk",
        "log",
        "zip",
        "docx",
    ]
    for (dirpath, _, filenames) in walk(data_dir, followlinks=True):
        for filename in filenames:
            # val = os.path.join(dirpath, filename)
            path = pathlib.Path(dirpath) / filename
            if (
                path.suffix[1:].lower() not in ignored_extensions
                and re.match(r"[0-9]{1,3}", path.suffix[1:]) is None
            ):
                file_dict = {}
                file_dict["index"] = "files"
                file_dict["name"] = filename
                file_dict["parent"] = str(path.parent)
                file_dict["path"] = str(path)
                file_dict["internal"] = internal
                stats = path.stat()
                file_dict["modify_time"] = stats.st_mtime
                file_dict["modify_time_h"] = datetime.datetime.fromtimestamp(
                    int(stats.st_mtime)
                ).strftime("%Y-%m-%dT%H:%M:%S%z")
                file_dict["size"] = stats.st_size
                file_dict["size_h"] = human_size(stats.st_size)
                file_dict["suffix"] = path.suffix[1:].lower()

                files.append(file_dict)
        # break

    elastic = elastic_calls.elastic_connection()
    elastic.indices.delete(index="files")

    elastic_calls.elastic_ingest(elastic=elastic, docs=files)


if __name__ == "__main__":
    main()
