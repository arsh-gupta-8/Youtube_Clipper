from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR

downloader = YoutubeCommentDownloader()

videoURL = "https://www.youtube.com/watch?v=8dTpNajxaH0" 

comments = downloader.get_comments_from_url(videoURL, sort_by=SORT_BY_POPULAR)

for index, comment in enumerate(comments):
    if index >= 10: 
        break
    print(f"[{comment['author']}]: {comment['text']}\n")