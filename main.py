from youtube_comment_downloader import YoutubeCommentDownloader, SORT_BY_POPULAR
from time import sleep
import re
import yt_dlp
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)
downloader = YoutubeCommentDownloader()
timeStampPattern = r"(?:(\d+):)?(\d+):(\d\d)"

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

  comments = downloader.get_comments_from_url(url, sort_by=SORT_BY_POPULAR)

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
          "title": "clips/" + get_video_title(url).replace(" ", "_")
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

  results = makeSegmentList(youtube_url)
  print(f"Found {len(results)} segments.")
  if results is None:
    return jsonify({"error": "Invalid YouTube URL"}), 400

  return jsonify({"success": True, "clips": results})


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

  try:
    download_video(videoURL, startTime, endTime, clipName, comment)
    return jsonify({
      "success": True, 
      "message": f"Successfully saved {clipName}"
    })
  except Exception as e:
    return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
  app.run(debug=True)