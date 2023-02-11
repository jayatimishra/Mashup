# Description: This program will download the audio from the first n videos of a YouTube search query and concatenate them into a single audio file.
import sys
from pytube import YouTube
from moviepy.editor import *
import moviepy.audio.fx.all as afx
import moviepy.audio.AudioClip as ac
from googleapiclient.discovery import build

import os
import requests
import threading



API_KEY = "AIzaSyD8R7vLoHl_4fX8b9bg523kNGiEhDD5IaY"

print(os.environ.get('API_KEY'))
print(os.environ)
def search_and_get_video_ids(query, n=5,key=API_KEY):
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&key={API_KEY}&type=video&q={query}&maxResults={n}'
    response = requests.get(url).json()
    video_ids = []
    for item in response['items']:
        video_ids.append(item['id']['videoId'])
    return video_ids


def download_audio(yt, m, i):
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_stream.download()
    audio_clip = AudioFileClip(audio_stream.default_filename)
    sub_audio_clip = audio_clip.subclip(0, m)
    sub_audio_clip.write_audiofile(f"{i}.mp3")
    print(f"Downloaded audio from video {i+1}: {yt.title}")

def download_and_concatenate_audio(video_ids, n=10, m=20):
    audio_clips = []
    # use multi-threading to download audio of all videos simultaneously and then concatenate them
    threads = []
    for i in range(n):
        video_id = video_ids[i]
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        thread = threading.Thread(target=download_audio, args=(yt, m, i))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    for i in range(n):
        audio_clip = AudioFileClip(f"{i}.mp3")
        audio_clips.append(audio_clip)
    final_audio = concatenate_audioclips(audio_clips)
    final_audio.write_audiofile("output.mp3")

    # remove all .mp3 files except the final output file
    for file in os.listdir(os.getcwd()):
        if file.endswith(".mp3") and file != "output.mp3":
            os.remove(file)

    # remove all .mp4 files
    for file in os.listdir(os.getcwd()):
        if file.endswith(".mp4"):
            os.remove(file)

def main(argv):
  if len(argv) != 4:
    print("Incorrect number of parameters. Please enter the correct number of parameters.")
    return
  singer_name = argv[0]
  number_of_videos = int(argv[1])
  audio_duration = int(argv[2])
  output_file = argv[3]
  video_ids = search_and_get_video_ids(singer_name, number_of_videos, API_KEY)
  download_and_concatenate_audio(video_ids, number_of_videos, audio_duration)



if __name__ == "__main__":
  main(sys.argv[1:])
