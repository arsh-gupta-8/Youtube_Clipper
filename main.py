from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from time import sleep
import re

downloader = YoutubeCommentDownloader()

videoURL = "https://www.youtube.com/watch?v=99lR1LpbBqA" 

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


for index, comment in enumerate(comments):
  if index == 500:
    break 
  timeStamp = re.search(timeStampPattern, comment['text'])
  if timeStamp:
    print(timeStamp.group())
    timeStamp = timeStamp.group()
    times.append(hms_to_seconds(hms=timeStamp))

# print(times)