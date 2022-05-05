import argparse
from convert_mp4_wav import mp4_to_wav
from split_instrument_vocal import split
from wav_diary import get_diary_raw_json
import json
from collections import defaultdict
import numpy as np
import os

def find_start_binary_search(time_intervals, left, right, target):
    while left < right:
        mid = (left + right) // 2
        start = time_intervals[mid][0]
        if start > target:
            right = mid
        else:
            left = mid + 1
        
    if left == 0:
        return time_intervals[0][0] <= target <= time_intervals[0][1]
    else:
        return time_intervals[left - 1][0] <= target <= time_intervals[left - 1][1] or time_intervals[left][0] <= target <= time_intervals[left][1]
    
def rawjson2json(raw_json, sample_interval):
    raw_json_content = raw_json['content']
    res_json = []
    audio_length = 0
    label_time_intervals = defaultdict(list)
    for content in raw_json_content:
        time_intervals = label_time_intervals[content['label']]
        start, end = content['segment']['start'], content['segment']['end']
        time_intervals.append([start, end])
        audio_length = max(audio_length, end)
    audio_length = int(audio_length)
    
    LABEL_NAMES = set(label_time_intervals.keys())

    for i in np.arange(0, audio_length, sample_interval):
        # count number of people that are talking
        occur_count = 0
        for label in LABEL_NAMES:
            if find_start_binary_search(label_time_intervals[label], 0, len(label_time_intervals[label]) - 1, i):
                occur_count += 1
        dump_info = {'millisecond': int(i * 1000),
                      'num_people_talking': occur_count}
        res_json.append(dump_info)
    return res_json

def main():
    p = argparse.ArgumentParser()
    p.add_argument('--model_path', '-m', type=str, default='vocalremover/models/baseline.pth')
#     p.add_argument('--input', '-i', required=True)
#     p.add_argument('--sr', '-r', type=int, default=44100)
#     p.add_argument('--n_fft', '-f', type=int, default=2048)
#     p.add_argument('--hop_length', '-H', type=int, default=1024)
#     p.add_argument('--batchsize', '-B', type=int, default=4)
#     p.add_argument('--cropsize', '-c', type=int, default=256)
#     p.add_argument('--output_image', '-I', action='store_true')
#     p.add_argument('--postprocess', '-p', action='store_true')
#     p.add_argument('--tta', '-t', action='store_true')
    
    p.add_argument('--mp4_path', '-p', type=str, required=True)
    p.add_argument('--save_json_dir', '-s', type=str, default='')
    p.add_argument('--sample_interval', '-i', type=float, default=1.0)
       
    args = p.parse_args()
    # load mp4 and convert to wav
    wav_path = mp4_to_wav(args.mp4_path)
    # split wav to instrument and vocal using vocal-remover
    instrument_wav_path, vocal_wav_path = split(wav_path, args.model_path, sr=44100, hop_length=1024, n_fft=2048, batchsize=4, cropsize=256)
    # diaryize parsed instrument wav
    raw_json = get_diary_raw_json(vocal_wav_path)
    
    # convert raw json to {'millisecond': xx, 'num_people_talking: xx} format
    res_json = rawjson2json(raw_json, args.sample_interval)
    
    # save res_json
    with open(os.path.join(args.save_json_dir, os.path.splitext(os.path.basename(wav_path))[0] + '.json'), 'w') as f:
        json.dump(res_json, f)
    
    
if __name__=='__main__':
    main()