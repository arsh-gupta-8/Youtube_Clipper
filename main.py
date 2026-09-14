from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from time import sleep
import re
import yt_dlp

downloader = YoutubeCommentDownloader()

videoTitle = "OhnePixel | How to fish"
videoURL = "https://www.youtube.com/watch?v=v7hiPMbNzrA" 

comments = downloader.get_comments_from_url(videoURL, sort_by=SORT_BY_POPULAR)
times = []

timeStampPattern = r"(?:(\d+):)?(\d+):(\d\d)"


def hms_to_seconds(hms):
  hms = hms.split(":")
  hms.reverse()
  seconds = 0
  for i in range(len(hms)):
    seconds += int(hms[i]) * (60**i)
  return seconds


def download_video(videoURL, startTime, endTime, clipName):
  ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    'external_downloader': 'ffmpeg',
    'external_downloader_args': {
        'ffmpeg_i': ['-ss', startTime, '-to', endTime]
    },
    'outtmpl': clipName,
    'overwrites': True 
  }

  print(f"🎬 Requesting segment from {startTime} to {endTime}...")

  confirmation = input(f"Do you want to download this segment? (y/n): ")
  if confirmation.lower() != 'y':
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([videoURL])
      
    print(f"✨ Download complete! Saved as: {clipName}")

    return 1

  return 0


for index, comment in enumerate(comments):
  if index == 500:
    break 
  timeStamp = re.search(timeStampPattern, comment['text'])
  if timeStamp:
    print(timeStamp.group())
    timeStamp = timeStamp.group()
    times.append(hms_to_seconds(hms=timeStamp))

# print(times)