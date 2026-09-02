from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from time import sleep

downloader = YoutubeCommentDownloader()

videoURL = "https://www.youtube.com/watch?v=99lR1LpbBqA" 

comments = downloader.get_comments_from_url(videoURL, sort_by=SORT_BY_POPULAR)
timeStampComments = []

for index, comment in enumerate(comments):
  print(index)
  if index == 500:
    break 
  if ":" in comment['text'] and (comment['text'][0].isdigit() or comment['text'][-1].isdigit()):
    timeStampComments.append(comment["text"])

print(timeStampComments)