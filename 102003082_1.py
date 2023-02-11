# Description: This program will download the audio from the first n videos of a YouTube search query and concatenate them into a single audio file.
import sys
from pytube import YouTube
from moviepy.editor import *
import moviepy.audio.fx.all as afx
import moviepy.audio.AudioClip as ac
from googleapiclient.discovery import build

from config import api_key
import os







def search_and_get_video_ids(query, n=5,key=api_key):
    
    youtube = build("youtube", "v3", key)

    
    request = youtube.search().list(part="id", type='video', q=query, maxResults=n)
    response = request.execute()

    video_ids = [item["id"]["videoId"] for item in response["items"]]

    return video_ids




def download_and_concatenate_audio(video_ids, n=10, m=20):
    audio_clips = []

    
    
    for i in range(n):
        video_id = video_ids[i]

        
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")

       
        audio_stream = yt.streams.filter(only_audio=True).first()

        
        audio_stream.download()

        
        audio_clip = AudioFileClip(audio_stream.default_filename)

        
        sub_audio_clip = audio_clip.subclip(0, m)

      
        audio_clips.append(sub_audio_clip)

        
        print(f"Downloaded audio from video {i+1}: {yt.title}")

    # Concatenating audio clips
    concatenated_audio = concatenate_audioclips(audio_clips)

  
    output_path = os.path.join(os.getcwd(), "output.mp3")
    concatenated_audio.write_audiofile(output_path)




def main(argv):
  if len(argv) != 4:
    print("Incorrect number of parameters. Please enter the correct number of parameters.")
    return
  
  singer_name = argv[0]
  number_of_videos = int(argv[1])
  audio_duration = int(argv[2])
  output_file = argv[3]


  video_ids = search_and_get_video_ids(singer_name, number_of_videos, api_key)
  download_and_concatenate_audio(video_ids, number_of_videos, audio_duration)



if __name__ == "__main__":
  main(sys.argv[1:])
