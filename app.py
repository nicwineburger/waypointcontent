import os
import json
import ast
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from pymediainfo import MediaInfo
import logging

logging.basicConfig(filename='flask_errors.log', level=logging.ERROR)

app = Flask(__name__)

db_path = os.path.join(os.path.abspath(os.path.dirname(__file__)),'instance/videos.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

db = SQLAlchemy(app)

class Video(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    source = db.Column(db.String(), nullable=False)
    file_name = db.Column(db.String(), nullable=False)
    file_extension = db.Column(db.String(), nullable=True)
    file_size = db.Column(db.String(), nullable=True)
    other_file_size = db.Column(db.String(), nullable=True)
    duration = db.Column(db.String(), nullable=True)
    other_duration = db.Column(db.String(), nullable=True)
    codecs_video = db.Column(db.String(), nullable=True)
    audio_codecs = db.Column(db.String(), nullable=True)

def get_video_files(root_directory):
    video_files = []
    print(f"Getting video files for {root_directory}")
    for root, dirs, files in os.walk(root_directory):
        for file in files:
            if file.lower().endswith('.temp.mp4'):
                continue
            if file.lower().endswith(('.mp4', '.mkv', '.avi', '.webm')):
                video_files.append(os.path.join(root, file))
    return video_files

def populate_database(root_directory, source_name):
    video_files = get_video_files(root_directory)
    existing_videos = Video.query.all()
    existing_file_names = {video.file_name for video in existing_videos}
    files_added = []
    
    for video_file in video_files:
        file_name, _ = os.path.splitext(os.path.basename(video_file))
        if file_name in existing_file_names:
 #           print(f"Video {file_name} already in database, skipping")
            continue
        
        print(f"Getting metadata for {video_file}")
        media_info = MediaInfo.parse(video_file)
        metadata = {}
        for track in media_info.tracks:
            if track.track_type == "General":
                for key, value in track.to_data().items():
                    metadata[key] = value
        
        video = Video(
            file_name=metadata["file_name"],
            file_extension=metadata["file_extension"],
            file_size=metadata["file_size"],
            other_file_size=str(metadata["other_file_size"]),
            duration=metadata["duration"],
            other_duration=str(metadata["other_duration"]),
            codecs_video=metadata["codecs_video"],
            audio_codecs=metadata["audio_codecs"],
            source=source_name
        )
        print(f"Adding metadata for {video_file} to database")
        db.session.add(video)
        db.session.commit()
        files_added.append(video.file_name)
    return files_added

@app.route('/')
def index():
    videos = Video.query.order_by(Video.source, Video.file_name).all()
    return render_template('index.html', videos=videos)

@app.route('/api/update_db')
def update():
    youtube_path = '/root/whatbox_mount/youtube'
    vice_path = '/root/whatbox_mount/vice'
    twitch_path = '/root/whatbox_mount/twitch'

    youtube_added = populate_database(youtube_path, 'youtube')
    vice_added = populate_database(vice_path, 'vice')
    twitch_added =  populate_database(twitch_path, 'twitch')

    return {'youtube': youtube_added, 'vice': vice_added, 'twitch': twitch_added}



if __name__ == '__main__':
    youtube_path = '/root/whatbox_mount/youtube'
    vice_path = '/root/whatbox_mount/vice'
    twitch_path = '/root/whatbox_mount/twitch'
    with app.app_context():
        db.create_all()
        populate_database(youtube_path, 'youtube')
        populate_database(vice_path, 'vice')
        populate_database(twitch_path, 'twitch')
    
    app.run(port=5000, debug=False)

