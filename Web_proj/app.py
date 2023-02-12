from flask import Flask, render_template, request
import os
import requests
import threading
import sys
from pytube import YouTube
from moviepy.editor import *

import moviepy.audio.fx.all as afx
import moviepy.audio.AudioClip as ac
from googleapiclient.discovery import build
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from flask import Flask, render_template, request
from wtforms import Form, IntegerField, StringField, validators

app = Flask(__name__)

API_KEY = os.environ.get('API_KEY')
USERNAME = os.environ.get('MAIL_USER')
PASSWORD = os.environ.get('MAIL_PASSWORD')

absolute_path = os.path.dirname(__file__)

relative_path = "output.mp3"
file_path = os.path.join(absolute_path, relative_path)

class InputForm(Form):
    singer_name = StringField('Singer Name', [validators.DataRequired(), validators.Length(min=3, max=50)])
    num_videos = IntegerField('Number of Videos', [validators.DataRequired(), validators.NumberRange(min=11, max=None)])
    duration = IntegerField('Duration of each Video', [validators.DataRequired(), validators.NumberRange(min=21, max=None)])
    email = StringField('Email ID', [validators.DataRequired(), validators.Email()])


@app.route('/download', methods=['GET', 'POST'])
def send_mp3_attachment():
    try:
        from_email = os.environ.get('MAIL_USER')
        password = os.environ.get('MAIL_PASSWORD')
        if not all([from_email, password]):
            raise Exception("Both FROM_EMAIL and EMAIL_PASSWORD environment variables must be set")

        # create a multipart message
        msg = MIMEMultipart()
        msg['From'] = from_email
        msg['To'] = to_email
       
        

        # open the file in bynary
        with open(file_path, 'rb') as f:
            # instance of MIMEBase and named as p
            p = MIMEBase('application', 'octet-stream')
            p.set_payload((f).read())
            # enconding into base64
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', "attachment; filename= %s" % file_path)
            msg.attach(p)

        # creates SMTP session
        s = smtplib.SMTP('smtp.gmail.com', 587)

        # start TLS for security
        s.starttls()

        # Authentication
        s.login(from_email, password)

        # sending the mail
        s.sendmail(from_email, to_email, msg.as_string())

        # terminating the session
        s.quit()
        print("Email sent successfully!")
    except Exception as e:
        print("Failed to send email: ", str(e))

@app.route('/', methods=['GET', 'POST'])
def index():
    form = InputForm(request.form)
    if request.method == 'POST' and form.validate():
        singer_name = form.singer_name.data
        num_videos = form.num_videos.data
        duration = form.duration.data
        email = form.email.data
        return '''
            Singer Name: {}<br>
            Number of Videos: {}<br>
            Duration of each Video: {}<br>
            Email ID: {}
        '''.format(singer_name, num_videos, duration, email)
         
        
        

        return 'Email sent to {} with result:<br><br>{}'.format(email, result)
    return render_template('home.html', form=form)

@app.route("/mashup", methods=["POST"])
def mashup():
    singer = request.form["singer"]
    num_videos = request.form["num_videos"]
    video_duration = request.form["video_duration"]
    email = request.form["email"]

    url = f'https://www.googleapis.com/youtube/v3/search?part=snippet&key={API_KEY}&type=video&q={singer}&maxResults={num_videos}'
    response = requests.get(url).json()
    video_ids = []
    for item in response['items']:
        video_ids.append(item['id']['videoId'])
        

    audio_clips = []
    # use multi-threading to download audio of all videos simultaneously and then concatenate them
    threads = []
    for i in range(num_videos):
        video_id = video_ids[i]
        yt = YouTube(f"https://www.youtube.com/watch?v={video_id}")
        thread = threading.Thread(target=download_audio, args=(yt, video_duration, i))
        threads.append(thread)
        thread.start()
    for thread in threads:
        thread.join()

    for i in range(num_videos):
        audio_clip = AudioFileClip(f"{i}.mp3")
        audio_clips.append(audio_clip)
    final_audio = concatenate_audioclips(audio_clips)
    SAVE_PATH = os.getcwd() + '/'
    file_path=SAVE_PATH + "output.mp3"
    final_audio.write_audiofile(file_path)
    

    # remove all .mp3 files except the final output file
    for file in os.listdir(os.getcwd()):
        if file.endswith(".mp3") and file != "output.mp3":
            os.remove(file)

    # remove all .mp4 files
    for file in os.listdir(os.getcwd()):
        if file.endswith(".mp4"):
            os.remove(file)
    
   

    # send email

    
    send_mp3_attachment(email,file_path)

    return "Result sent to email!"

if __name__ == "__main__":
    app.run()
