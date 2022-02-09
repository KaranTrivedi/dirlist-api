#!./venv/bin/python

"""
Test
"""

import youtube_dl as yt

def main():
    """
    main
    """

    name = "/hdd1/media/movies/dimid/edits/test"
    url = "https://www.youtube.com/watch?v=tPEE9ZwTmy0"

    if name:
        name = f"{name}.%(ext)s"
    else:
        name = "%(title)s.%(ext)s"

    ydl_opts = {
        "outtmpl": name,
        "quiet": True
    }

    with yt.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])

if __name__ == "__main__":
    main()