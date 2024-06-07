# 下面是如何跑rhubarb将语音转化成为嘴型时间轴

import asyncio
import time
import subprocess
import os

"""
使用本地的Rhubarb Lip Sync工具指批量生成嘴唇时间轴。
"""

start = time.time()
wave_dir = 'g:/fretdance介绍视频音源/视频二'
# 遍历所有wav文件
for root, dirs, files in os.walk(wave_dir):
    for file in files:
        if file.endswith('.wav'):
            wav_file = os.path.join(root, file)
            output = f'g:/fretdance介绍视频音源/视频二/{file[:-4]}.json'
            subprocess.run(['G:\Rhubarb-Lip-Sync-1.13.0-Windows\\rhubarb.exe', '-r', 'phonetic', '-f', 'json', '--datUsePrestonBlair', '-o', output,
                            wav_file], shell=True)


finish = time.time()

print(f'Finished in {finish - start} seconds')


def apply_lip_sync():
    # 下面是一个简单的示例，演示如何读取嘴唇时间轴并将其应用于角色的形状键。
    # 在blender中使用./blender/lip_sync.py脚本，将嘴唇时间轴应用到角色的形状键上。

    def lerp(a, b, t):
        return a + (b - a) * t

    async def apply_shape_key(mouth_cues, transition_time=0.1):
        current_time = 0
        current_keyframe = 0
        num_keyframes = len(mouth_cues)

        while current_keyframe < num_keyframes - 1:
            start_time = mouth_cues[current_keyframe]['start']
            start_value = mouth_cues[current_keyframe]['value']
            end_value = mouth_cues[current_keyframe + 1]['value']

            # 等待直到开始时间
            while current_time < start_time:
                await asyncio.sleep(0.01)
                current_time += 0.01

            # 应用开始值
            print(f"Applying shape key: {start_value}")

            # 在过渡时间内平滑过渡到结束值
            transition_start_time = current_time
            while current_time < transition_start_time + transition_time:
                t = (current_time - transition_start_time) / transition_time
                interpolated_value = lerp(start_value, end_value, t)
                print(f"Applying interpolated shape key: {interpolated_value}")
                await asyncio.sleep(0.01)
                current_time += 0.01

            # 应用结束值
            print(f"Applying shape key: {end_value}")

            current_keyframe += 1

        # 等待直到最后一个结束时间
        while current_time < mouth_cues[-1]['end']:
            await asyncio.sleep(0.01)
            current_time += 0.01

    mouthCues = [
        {"start": 0.00, "end": 0.10, "value": "B"},
        {"start": 0.10, "end": 0.24, "value": "F"},
        {"start": 0.24, "end": 0.59, "value": "B"},
        {"start": 0.59, "end": 0.73, "value": "C"},
        {"start": 0.73, "end": 0.80, "value": "B"},
        {"start": 0.80, "end": 0.88, "value": "A"},
        {"start": 0.88, "end": 0.97, "value": "H"},
        {"start": 0.97, "end": 1.11, "value": "C"},
        {"start": 1.11, "end": 1.32, "value": "B"},
        {"start": 1.32, "end": 1.39, "value": "C"},
        {"start": 1.39, "end": 1.48, "value": "A"},
        {"start": 1.48, "end": 1.55, "value": "B"},
        {"start": 1.55, "end": 1.76, "value": "C"},
        {"start": 1.76, "end": 2.25, "value": "B"},
        {"start": 2.25, "end": 2.53, "value": "F"},
        {"start": 2.53, "end": 2.60, "value": "C"},
        {"start": 2.60, "end": 3.02, "value": "E"},
        {"start": 3.02, "end": 3.09, "value": "G"},
        {"start": 3.09, "end": 3.16, "value": "C"},
        {"start": 3.16, "end": 3.30, "value": "B"},
        {"start": 3.30, "end": 3.44, "value": "F"},
        {"start": 3.44, "end": 3.58, "value": "B"},
        {"start": 3.58, "end": 3.66, "value": "A"},
        {"start": 3.66, "end": 3.72, "value": "B"},
        {"start": 3.72, "end": 3.85, "value": "E"},
        {"start": 3.85, "end": 3.92, "value": "F"},
        {"start": 3.92, "end": 4.22, "value": "X"}
    ]

    apply_shape_key(mouthCues)
