import os
from moviepy.editor import VideoFileClip

def mp4_to_wav(mp4_path):
    video = VideoFileClip(mp4_path)
    audio = video.audio
    save_dir = os.path.split(mp4_path)[0]
    file_name = os.path.splitext(os.path.basename(mp4_path))[0]
    wav_save_dir = os.path.join(save_dir, file_name + '.wav')
    audio.write_audiofile(wav_save_dir)
    return wav_save_dir
    