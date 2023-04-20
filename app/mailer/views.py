#!./venv/bin/python

"""
Api for mailer page
"""

from fastapi import APIRouter
import logging
from libs import mailer_calls
from libs import local_calls

import json

mailer_router = APIRouter()

logger = logging.getLogger(__name__)

@mailer_router.post("/generic", tags=["mailer"])
def generic(blob: dict):
    """
    generic endpoint for mailer.\n

    Returns:\n
        Subject: Generic Mailer\n
        Message: blob\n
    """

    return mailer_calls.mailer("Generic Mailer", json.dumps(blob, indent=2))

@mailer_router.post("/movies", tags=["mailer"])
def movies(blob: dict):
    """
    sonarr endpoint for movies.\n

    Returns:\n
        {
            "movie": {
                "id": 8,
                "title": "Gone Girl",
                "year": 2014,
                "releaseDate": "2015-01-15",
                "folderPath": "/hdd1/media/movies/Gone Girl (2014)",
                "tmdbId": 210577,
                "imdbId": "tt2267998"
            },
            "remoteMovie": {
                "tmdbId": 210577,
                "imdbId": "tt2267998",
                "title": "Gone Girl",
                "year": 2014
            },
            "movieFile": {
                "id": 4,
                "relativePath": "Gone.Girl.2014.1080p.Remux.AVC.DTS-HD.MA.7.1-ShocK.mkv",
                "path": "/hdd1/transmission/finished/Gone.Girl.2014.1080p.Remux.AVC.DTS-HD.MA.7.1-ShocK.mkv",
                "quality": "Remux-1080p",
                "qualityVersion": 1,
                "releaseGroup": "ShocK",
                "sceneName": "Gone.Girl.2014.1080p.Remux.AVC.DTS-HD.MA.7.1-ShocK",
                "indexerFlags": "G_Freeleech",
                "size": 39529720162,
                "dateAdded": "2023-01-15T20:22:46.1316954Z",
                "mediaInfo": {
                "audioChannels": 7.1,
                "audioCodec": "DTS-HD MA",
                "audioLanguages": [
                    "eng"
                ],
                "height": 1080,
                "width": 1920,
                "subtitles": [
                    "eng",
                    "spa",
                    "dan",
                    "fin",
                    "nor",
                    "rus",
                    "swe",
                    "zho",
                    "est",
                    "ind",
                    "kor",
                    "lav",
                    "lit",
                    "msa",
                    "tha",
                    "ukr",
                    "vie"
                ],
                "videoCodec": "AVC",
                "videoDynamicRange": "",
                "videoDynamicRangeType": ""
                }
            },
            "isUpgrade": false,
            "downloadClient": "transmission",
            "downloadClientType": "Transmission",
            "downloadId": "46BAFF01BCF576C04A9E9E19293F2D7492A4D583",
            "eventType": "Download",
            "instanceName": "Radarr"
        }
    """

    try:
        subject = f'{blob["movie"]["title"]} - {blob["eventType"]}'
    except Exception as exp:
        logger.exception(exp)
        logger.info(json.dumps(blob, indent=2))

    if blob["eventType"] in ['Download', 'Grab']:
        message = {
            "size": local_calls.human_size(blob["movieFile"]["size"]),
            "payload": blob
        }
    # logger.exception(exp)
        message = json.dumps(message, indent=2)
    else:
        message = json.dumps(blob, indent=2)

    return mailer_calls.mailer(subject, message)

@mailer_router.post("/shows", tags=["mailer"])
def shows(blob: dict):
    """
    sonarr endpoint for shows.\n

    Returns:\n
        {
            "series": {
                "id": 148,
                "title": "Vinland Saga",
                "path": "/hdd1/media/shows/Vinland Saga",
                "tvdbId": 359274,
                "tvMazeId": 42155,
                "imdbId": "tt10233448",
                "type": "standard"
            },
            "episodes": [
                {
                "id": 13125,
                "episodeNumber": 2,
                "seasonNumber": 2,
                "title": "Ketil's Farm",
                "airDate": "2023-01-17",
                "airDateUtc": "2023-01-16T15:30:00Z"
                }
            ],
            "episodeFile": {
                "id": 5119,
                "relativePath": "Season 2/S02E02 - Ketil's Farm HDTV-720p.mkv",
                "path": "/hdd1/transmission/finished/[Erai-raws] Vinland Saga Season 2 - 02 [720p][80BB44B3]/[Erai-raws] Vinland Saga Season 2 - 02 [720p][Multiple Subtitle][80BB44B3].mkv",
                "quality": "HDTV-720p",
                "qualityVersion": 1,
                "releaseGroup": "Erai-raws",
                "sceneName": "[Erai-raws] Vinland Saga Season 2 - 02 [720p][80BB44B3]",
                "size": 808782609
            },
            "isUpgrade": false,
            "downloadClient": "transmission",
            "downloadClientType": "Transmission",
            "downloadId": "AE561DE97732AF7E5910746555CCE82B0CACBB1F",
            "eventType": "Download"
        }
    """

    try:
        title = (blob["series"]["title"][:75] + '..') if len(blob["series"]["title"]) > 75 else blob["series"]["title"]
        subject = f'{title} - S{blob["episodes"][0]["seasonNumber"]}E{blob["episodes"][0]["episodeNumber"]} - {blob["eventType"]}'
    except KeyError as exp:
        title = (blob["series"]["title"][:75] + '..') if len(blob["series"]["title"]) > 75 else blob["series"]["title"]
        subject = f'{title} - {blob["eventType"]}'
    except Exception as exp:
        logger.exception(exp)
        subject = f"{title} Show Execption"
        body = {
            "error": str(exp),
            "data": blob
        }
        message = json.dumps(body, indent=2)
        return mailer_calls.mailer(subject, message)

    if blob["eventType"] in ['Download', 'Grab']:
        message = {
            "size": local_calls.human_size(blob["episodeFile"]["size"]),
            "payload": blob
        }
    # logger.exception(exp)
        message = json.dumps(message, indent=2)
    else:
        message = json.dumps(blob, indent=2)

    return mailer_calls.mailer(subject, message)
