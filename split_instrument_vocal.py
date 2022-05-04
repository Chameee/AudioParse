from vocalremover.inference import run_silent 

def split(wav_path, model_path, sr=44100, hop_length=1024, n_fft=2048, batchsize=4, cropsize=256):
    return run_silent(wav_path, model_path, sr, hop_length, n_fft, batchsize, cropsize)




