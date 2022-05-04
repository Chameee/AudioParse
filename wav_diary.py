from pyannote.audio import Pipeline
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")

def get_diary_raw_json(wav_path):
    diary = pipeline(wav_path)
    return diary.for_json()


 
    

