#!/venv/bin/python
"""
Read dirs and folders into elasticsearch.
"""

# DEFAULTS
import configparser
import logging

import elastic_calls

import json
from os.path import isfile, join
from os import walk
import os
import pathlib
import re
import datetime

# Define config and logger.
CONFIG = configparser.ConfigParser()
CONFIG.read('conf/config.ini')
SECTION = 'dir_loader'

def human_size(num, suffix="B"):
    """
    Convert bytes to human readable format
    """
    for unit in ["", "Ki", "Mi", "Gi", "Ti", "Pi", "Ei", "Zi"]:
        if abs(num) < 1024.0:
            return "%3.1f%s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f%s%s" % (num, "Yi", suffix)

def show_sections(logger):
    '''
    Output all options for given section
    '''

    conf_str = "\n\n"
    for sect in CONFIG.sections():
        conf_str += "[" + sect + "]\n"
        for var in list(CONFIG[sect]):
            conf_str += var + "\t\t=\t" + CONFIG[sect][var] + "\n"
    logger.info(conf_str)


def main():
    '''
    Main function.
    '''

    # http://www.costafarms.com/get-growing/news/perennial-flowers-bloom-guide

    logging.basicConfig(filename=CONFIG[SECTION]['log'],
                        level=CONFIG[SECTION]['level'],
                        format='%(asctime)s::%(name)s::%(funcName)s::%(levelname)s::%(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    logger = logging.getLogger(SECTION)
    logger.info("####################STARTING####################")

    if CONFIG[SECTION]['level'] == "DEBUG":
        show_sections(logger=logger)

    internal = "G:\\4. Videos"
    data_dir = "data"
    files = []
    ignored_extensions = ["txt", "sfv", "py", "jpg", "png", "srt", "nfo", "tbn", "ico",
                          "ssa", "website", "old", "bat", "iso", "torrent", "db", "rar",
                          "cue", "idk", "log", "zip", "docx"]
    for (dirpath, _, filenames) in walk(data_dir, followlinks=True):
        for filename in filenames:
            # val = os.path.join(dirpath, filename)
            path = pathlib.Path(dirpath) / filename
            if path.suffix[1:].lower() not in ignored_extensions and re.match("r[0-9]{1,3}", path.suffix[1:]) is None:
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

    elastic = elastic_calls.elastic_connection(logger=logger)
    elastic.indices.delete(index='files')

    elastic_calls.elastic_ingest(elastic=elastic, logger=logger, docs=files)


if __name__ == "__main__":
    main()
