from flask import Flask, render_template, request
import os
import requests
import threading

from pytube import YouTube
from moviepy.editor import *

from sendoutput import *
import moviepy.audio.fx.all as afx
import moviepy.audio.AudioClip as ac
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
from flask import Flask, render_template, request
from wtforms import Form, IntegerField, StringField, validators

app = Flask(__name__)

absolute_path = os.path.dirname(__file__)

relative_path = "output.mp3"
file_path = os.path.join(absolute_path, relative_path)

class InputForm(Form):
    singer_name = StringField('Singer Name', [validators.DataRequired(), validators.Length(min=3, max=50)])
    num_videos = IntegerField('Number of Videos', [validators.DataRequired(), validators.NumberRange(min=11, max=None)])
    duration = IntegerField('Duration of each Video', [validators.DataRequired(), validators.NumberRange(min=21, max=None)])
    email = StringField('Email ID', [validators.DataRequired(), validators.Email()])


@app.route('/', methods=['GET', 'POST'])
def index():
    form = InputForm(request.form)
    if request.method == 'POST' and form.validate():
        singer_name = form.singer_name.data
        num_videos = form.num_videos.data
        duration = form.duration.data
        email = form.email.data
        
        # download and send the mp3 file
        # download_mp3(singer_name, num_videos, duration, email)
        # call above function as a background process
        threading.Thread(target=download_mp3, args=(singer_name, num_videos, duration, email)).start()
        return '''
            Singer Name: {}<br>
            Number of Videos: {}<br>
            Duration of each Video: {}<br>
            Email ID: {}
        '''.format(singer_name, num_videos, duration, email)
    return render_template('home.html', form=form)


if __name__ == "__main__":
    app.run()
