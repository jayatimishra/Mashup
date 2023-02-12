from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pytube import YouTube
from moviepy.editor import *
import moviepy.audio.fx.all as afx
import moviepy.audio.AudioClip as ac
import random
import os
import requests
import string
import threading
import smtplib

API_KEY = os.environ.get('API_KEY')
USERNAME = os.environ.get('MAIL_USER')
PASSWORD = os.environ.get('MAIL_PASSWORD')

# create a media folder to store the downloaded audio files
if not os.path.exists('media'):
    os.mkdir('media')

MEDIA_FOLDER = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'media')
print(MEDIA_FOLDER)
def search_and_get_video_ids(query, n=5,key=API_KEY):
    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&key={API_KEY}&type=video&q={query}&maxResults={n}'
    response = requests.get(url).json()
    video_ids = []
    for item in response['items']:
        video_ids.append(item['id']['videoId'])
    return video_ids


def download_audio(yt, m, i, file_name):
    audio_stream = yt.streams.filter(only_audio=True).first()
    audio_stream.download(MEDIA_FOLDER)
    audio_clip = AudioFileClip(f"{MEDIA_FOLDER}/{audio_stream.default_filename}")
    sub_audio_clip = audio_clip.subclip(0, m)
    sub_audio_clip.write_audiofile(f"{MEDIA_FOLDER}/{i}_{file_name}.mp3")
    print(f"Downloaded audio from video {i+1}: {yt.title}")

def download_and_concatenate_audio(video_ids, file_name, n=10, m=20):
    audio_clips = []
    # use multi-threading to download audio of all videos simultaneously and then concatenate them
    threads = []
    for i in range(n):
        video_id = video_ids[i]
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        thread = threading.Thread(target=download_audio, args=(yt, m, i, file_name))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    for i in range(n):
        audio_clip = AudioFileClip(f"{MEDIA_FOLDER}/{i}_{file_name}.mp3")
        audio_clips.append(audio_clip)
    final_audio = concatenate_audioclips(audio_clips)
    final_audio.write_audiofile(f"{file_name}.mp3")

def download_mp3(singer_name, number_vid, duration, customer_email):
    number_of_videos = number_vid
    if number_of_videos<10:
        print("Please enter a number greater than 10.")
        return
    audio_duration = duration
    if audio_duration<20:
        print("Please enter a number greater than 20.")
        return
    # create a unique string
    unique_string = ''.join(random.choices(string.ascii_uppercase + string.digits, k=5))
    file_name = f"{customer_email}_{unique_string}"
    video_ids = search_and_get_video_ids(singer_name, number_of_videos, API_KEY)
    download_and_concatenate_audio(video_ids, file_name, number_of_videos, audio_duration)

    # zip the above file
    os.system(f"zip {file_name}.zip {file_name}.mp3")

    # send the zip file to the customer's email
    sender_email = USERNAME
    receiver_email = customer_email
    password = PASSWORD
    message = f"""\Hi {customer_email}, \n\n Your audio file is ready. Please find the attachment. \n\n Regards, \n Jayati Mishra"""
    server = smtplib.SMTP('smtp.gmail.com', 587)
    # attach the zip file to the email
    with open(f"{file_name}.zip", "rb") as attachment:
        part = MIMEBase("application", "octet-stream")
        part.set_payload(attachment.read())
    encoders.encode_base64(part)
    part.add_header(
        "Content-Disposition",
        f"attachment; filename= {file_name}.zip",
    )
    msg = MIMEMultipart()
    msg.attach(part)
    msg.attach(MIMEText(message, "plain"))
    server.starttls()
    server.login(sender_email, password)
    server.sendmail(sender_email, receiver_email, msg.as_string())
    server.quit()
    print("Mail sent!!!")
    # remove all .mp3 files except the final output file
    for file in os.listdir(MEDIA_FOLDER):
        if file.endswith(".mp3"):
            os.remove(f"{MEDIA_FOLDER}/{file}")
    os.remove(f"{file_name}.mp3")

    # remove all .mp4 files
    for file in os.listdir(MEDIA_FOLDER):
        if file.endswith(".mp4"):
            os.remove(f"{MEDIA_FOLDER}/{file}")
    os.remove(f"{file_name}.zip")