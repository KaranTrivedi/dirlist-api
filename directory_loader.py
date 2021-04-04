#!./venv/bin/python
"""
Read dirs and folders into elasticsearch.
"""

import configparser
import datetime
import logging
import os
import sys
import json
import pathlib
import re
from os import walk

os.chdir("/home/karan/projects/dirlist-api")
import libs.local_calls as local_calls
import libs.elastic_calls as elastic_calls

import start

# Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read("conf/config.ini")

SECTION = "dir_loader"
IP = CONFIG['global']["ip"]
PORT = CONFIG['global']["port"]

logger = logging.getLogger(SECTION)

DATA_PATH = CONFIG["global"]["data_path"]

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
        datefmt="%Y-%m-%dT%H:%M:%S%z",
    )

    logger.info("####################STARTING####################")

    files = []
    ignored_extensions = [
        # "txt",
        # "sfv",
        # "py",
        # "jpg",
        # "png",
        # "srt",
        # "nfo",
        # "tbn",
        # "ico",
        # "ssa",
        # "website",
        # "old",
        # "bat",
        # "iso",
        # "torrent",
        # "db",
        # "rar",
        # "cue",
        # "idk",
        # "log",
        # "zip",
        # "docx",
        # "js",
        # "rb",
        # "md",
        # "json",
        # "uc",
        # "html",
        # "xnb",
        # "svg",
        # "",
    ]
    for (dirpath, _, filenames) in walk(DATA_PATH, followlinks=True):
        for filename in filenames:
            # val = os.path.join(dirpath, filename)
            path = pathlib.Path(dirpath) / filename
            if (path.suffix[1:].lower() not in ignored_extensions
                    and re.match(r"[0-9]{1,3}", path.suffix[1:]) is None
                ):
                file_dict = {}
                file_dict["index"] = start.CONFIG["dir_loader"]["index"]
                file_dict["name"] = filename
                file_dict["parent"] = str(path.parent)[len(DATA_PATH):] + "/"
                file_dict["path"] = str(path)[len(DATA_PATH):]
                file_dict["url"] = "http://" + start.IP + ":" + start.PORT + "/directory/" + \
                    str(path)[len(DATA_PATH):]
                stats = path.stat()
                file_dict["modify_time"] = stats.st_mtime*1000
                file_dict["modify_time_h"] = datetime.datetime.fromtimestamp(
                    int(stats.st_mtime)
                ).strftime("%Y-%m-%dT%H:%M:%S%z")
                file_dict["size"] = stats.st_size
                file_dict["size_h"] = local_calls.human_size(stats.st_size)
                file_dict["ext"] = path.suffix[1:].lower()

                files.append(file_dict)
                logger.debug(json.dumps(file_dict, indent=2))
                # sys.exit()
        # break

    elastic = elastic_calls.elastic_connection()
    elastic.indices.delete(index=start.CONFIG["dir_loader"]["index"])
    elastic_calls.elastic_ingest(elastic=elastic, docs=files)

    sys.exit()

if __name__ == "__main__":
    main()
