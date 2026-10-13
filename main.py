from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from time import sleep
import re
import yt_dlp
from flask import Flask, render_template, request, jsonify
import concurrent.futures

app = Flask(__name__)
downloader = YoutubeCommentDownloader()
timeStampPattern = r"(?:(\d+):)?(\d+):(\d\d)"
executor = concurrent.futures.ThreadPoolExecutor(max_workers=4)
times = []


def get_video_title(url):
  """Fetches the video title without downloading the video stream."""
  ydl_opts = {
    'quiet': True,
    'no_warnings': True,
    'skip_download': True
  }
  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=False)
      return info.get('title', 'Unknown Title')
  except Exception as e:
    print(f"Error fetching title: {e}")
    return "YouTube Video Highlights"


def get_comments_yt_dlp(url, max_comments=500):
  ydl_opts = {
    'getcomments': True,
    'skip_download': True,
    'extract_flat': True,
    'quiet': True,
  }
  try:
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
      info = ydl.extract_info(url, download=False)
      return [{'text': c.get('text', '')} for c in info.get('comments', [])[:max_comments]]
  except Exception as e:
    print(f"Error fetching comments: {e}")
    return []


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
    'format': 'bestvideo[vcodec^=avc1]+bestaudio[acodec^=mp4a]/best[vcodec^=avc1]',
    'external_downloader': 'ffmpeg',
    'external_downloader_args': {
        'ffmpeg_i': ['-ss', startTime, '-to', endTime]
    },
    'outtmpl': clipName,
    'overwrites': True 
  }

  print(f"Requesting segment from {startTime} to {endTime}...")
  print(f"Comment: {comment}")

  with yt_dlp.YoutubeDL(ydl_opts) as ydl:
    ydl.download([videoURL])
    
  print(f"Download complete! Saved as: {clipName}")

  return 1


def run_download_task(videoURL, startTime, endTime, clipName, comment):
  try:
    download_video(videoURL, startTime, endTime, clipName, comment)
    print(f"[Thread Success] Downloaded: {clipName}")
  except Exception as e:
    print(f"[Thread Error] Failed downloading {clipName}: {e}")


# for index, comment in enumerate(comments):
#   if index == 500:
#     break 
#   timeStamp = re.search(timeStampPattern, comment['text'])
#   YTcomment = comment['text']
#   if timeStamp:
#     timeStamp = timeStamp.group()
#     clipped = False
#     for clipTime in times:
#       if hms_to_seconds(hms=timeStamp) in range(clipTime - 30, clipTime + 30):
#         clipped = True
#         break
#     if not clipped and hms_to_seconds(hms=timeStamp) > 30:
#       dwnldNumber += download_video(videoURL=videoURL, startTime=seconds_to_hms(hms_to_seconds(hms=timeStamp) - 30), endTime=seconds_to_hms(hms_to_seconds(hms=timeStamp) + 30), clipName=f"{videoTitle}_{dwnldNumber}.mp4", comment=YTcomment)
#       times.append(hms_to_seconds(hms=timeStamp))


def makeSegmentList(url):
  times.clear()

  # comments = downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR)
  comments = get_comments_yt_dlp(url, max_comments=500)
  comments_list = list(comments)
  print(f"Total comments fetched: {len(comments_list)}")

  for index, comment in enumerate(comments):
    if index > 500:
      break 
    timeStamp = re.search(timeStampPattern, comment['text'])
    YTcomment = comment['text']
    if timeStamp:
      timeStamp = timeStamp.group()
      clipped = False
      hmsTime = hms_to_seconds(hms=timeStamp)
      for clipTime in times:
        if hmsTime in range(clipTime['clipTime'] - 30, clipTime['clipTime'] + 30):
          clipped = True
          break
      if not clipped and hmsTime > 30:
        times.append({
          "startTime": seconds_to_hms(hmsTime - 30),
          "endTime": seconds_to_hms(hmsTime + 30),
          "clipTime": hmsTime,
          "url": f"{url}&t={hmsTime}s",
          "comment": YTcomment,
        })

  return times


@app.route('/')
def index():
  return render_template('index.html')


@app.route('/process-url', methods=['POST'])
def process_url():
  data = request.get_json()
  youtube_url = data.get('url')

  if not youtube_url:
    return jsonify({"error": "No URL provided"}), 400

  try:
    video_title = get_video_title(youtube_url)
    results = makeSegmentList(youtube_url)
    print(f"Found {len(results)} segments.")

    return jsonify({
        "success": True, 
        "videoTitle": video_title,
        "clips": results
    })
  except Exception as e:
    return jsonify({"error": str(e)}), 500


@app.route('/download-clip', methods=['POST'])
def download_clip():
  data = request.get_json()
  videoURL = data.get('url')
  startTime = data.get('startTime')
  endTime = data.get('endTime')
  clipName = data.get('clipName')
  comment = data.get('comment')

  if not all([videoURL, startTime, endTime, clipName]):
    return jsonify({"error": "Missing required parameters"}), 400

  executor.submit(run_download_task, videoURL, startTime, endTime, clipName, comment)

  return jsonify({
    "success": True, 
    "message": f"Started the downlaod for {clipName} in a thread"
  })


if __name__ == '__main__':
  app.run(debug=True)