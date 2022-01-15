from http.client import InvalidURL
import requests
import sys
import re
import json
import subprocess
from slugify import slugify


ua = "redlr:0.1 (by /u/Tygha)"

# url = input("Post Url: ")

if len(sys.argv) > 0:
    url = sys.argv[1]
else:
    url = input("Post URL: ")

# GET URL JSON

try:
    print("Getting information...")
    req = requests.get(url+".json", headers={'User-agent': ua})
    content = json.loads(req.content)
except (requests.exceptions.MissingSchema, requests.exceptions.ConnectionError, InvalidURL) as e:
    print("Error.\n")
    quit()

try:
    # PARSE JSON TO GET VIDEO AUDIO URLS
    vid_url = content[0]["data"]["children"][0]["data"]["secure_media"]["reddit_video"]["fallback_url"]
    audio_url = re.sub(r"(?<=_)[0-9]+", "audio", vid_url)
except TypeError as e:
    print("Could not get video")
    quit()

subreddit = slugify(content[0]["data"]["children"][0]["data"]["subreddit"])
posted_by = slugify(content[0]["data"]["children"][0]["data"]["author"])
title = slugify(content[0]["data"]["children"][0]["data"]["title"])

print(f"r/{subreddit} by {posted_by}: {title}")


fn = f"{title}_by_{posted_by}_at_{subreddit}.mp4"

# GET VIDEO AND AUDIO
print("Downloading video...")
video = requests.get(vid_url)
print("Downloading audio...")
audio = requests.get(audio_url)

# SAVE VIDEO AND AUDIO TO FILES
with open("tmp.mp4", "wb") as fp:
    fp.write(video.content)

with open("tmp.mp3", "wb") as fp:
    fp.write(audio.content)

# MERGE VIDEO AND AUDIO
command = f"ffmpeg --disabledebug -i tmp.mp4 -i tmp.mp3 -c:v copy -c:a aac {fn}".split(
)
print("Merging audio and video...")
subprocess.call(command, shell=True)

print(f"saved as {fn}")
# CLEANUP
subprocess.call("rm tmp.mp4 tmp.mp3", shell=True)
