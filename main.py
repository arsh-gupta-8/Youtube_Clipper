from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from time import sleep
import re
import yt_dlp

downloader = YoutubeCommentDownloader()

videoTitle = "Jynxzi | 3v3 mode"
videoURL = "https://www.youtube.com/watch?v=oF9Tm4LXm3o" 

comments = downloader.get_comments_from_url(videoURL, sort_by=SORT_BY_POPULAR)
times = []
dwnldNumber = 0

timeStampPattern = r"(?:(\d+):)?(\d+):(\d\d)"


def hms_to_seconds(hms):
  hms = hms.split(":")
  hms.reverse()
  seconds = 0
  for i in range(len(hms)):
    seconds += int(hms[i]) * (60**i)
  return seconds


def seconds_to_hms(seconds):
  h = seconds // 3600
  m = (seconds % 3600) // 60
  s = seconds % 60
  if h > 0:
    return f"{h}:{m:02d}:{s:02d}"
  return f"{m:02d}:{s:02d}"


def download_video(videoURL, startTime, endTime, clipName, comment):
  ydl_opts = {
    'format': 'bestvideo+bestaudio/best',
    'external_downloader': 'ffmpeg',
    'external_downloader_args': {
        'ffmpeg_i': ['-ss', startTime, '-to', endTime]
    },
    'outtmpl': clipName,
    'overwrites': True 
  }

  print(f"Requesting segment from {startTime} to {endTime}...")
  print(f"Comment: {comment}")

  confirmation = input(f"Do you want to download this segment? (y/n): ")
  if confirmation.lower() == 'y':
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      ydl.download([videoURL])
      
    print(f"Download complete! Saved as: {clipName}")

    return 1

  return 0


for index, comment in enumerate(comments):
  if index == 500:
    break 
  timeStamp = re.search(timeStampPattern, comment['text'])
  YTcomment = comment['text']
  if timeStamp:
    timeStamp = timeStamp.group()
    clipped = False
    for clipTime in times:
      if hms_to_seconds(hms=timeStamp) in range(clipTime - 30, clipTime + 30):
        clipped = True
        break
    if not clipped and hms_to_seconds(hms=timeStamp) > 30:
      dwnldNumber += download_video(videoURL=videoURL, startTime=seconds_to_hms(hms_to_seconds(hms=timeStamp) - 30), endTime=seconds_to_hms(hms_to_seconds(hms=timeStamp) + 30), clipName=f"{videoTitle}_{dwnldNumber}.mp4", comment=YTcomment)
      times.append(hms_to_seconds(hms=timeStamp))

# print(times)