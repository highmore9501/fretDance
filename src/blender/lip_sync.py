import bpy
import os
import json

"""
脚本的作用是给readyplay.me的avatar添加嘴唇动作
需要提前把lip_sync_info生成，放在某个文件夹下
lip_sync_info生成的方法可以使用./utils/make_lip_sync_info.py
"""

value_map = {
    "A": "viseme_PP",
    "B": "viseme_SS",
    "C": "viseme_E",
    "D": "viseme_aa",
    "E": "viseme_O",
    "F": "viseme_U",
    "G": "viseme_FF",
    "H": "viseme_RR",
    "X": "None"
}

all_visemes = ["viseme_PP", "viseme_SS", "viseme_E", "viseme_aa",
               "viseme_O", "viseme_U", "viseme_FF", "viseme_RR"]

FPS = 30

# 获取当前的 Sequencer 编辑器
sequencer_editor = bpy.context.scene.sequence_editor


def clear_all_shapekey(mesh_name):
    ob = bpy.data.objects[mesh_name]
    if hasattr(ob.data, "shape_keys"):
        if ob.data.shape_keys and ob.data.shape_keys.animation_data and ob.data.shape_keys.animation_data.action:
            for fcurve in ob.data.shape_keys.animation_data.action.fcurves:
                fcurve.keyframe_points.clear()


def main(lip_sync_info_dir, mesh_name):
    avatar_mesh = bpy.data.objects[mesh_name]
    # 确保 Sequencer 编辑器已经打开
    if sequencer_editor:
        # 获取 Sequencer 中的所有序列
        sequences = sequencer_editor.sequences

        # 遍历所有序列
        for sequence in sequences:
            # 检查序列是否为音频序列
            if sequence.type == 'SOUND':
                # 获取音频序列的文件名
                audio_file_name = sequence.sound.name

                # 获取音频序列的开始时间点
                audio_start_frame = sequence.frame_start

                lip_sync_info_file = os.path.join(
                    lip_sync_info_dir, audio_file_name.split('.')[0] + '.json')

                print(f'当前音频是：{audio_file_name}，开始时间点是：{audio_start_frame}')

                with open(lip_sync_info_file, 'r') as f:
                    data = json.load(f)
                    mouthCues = data['mouthCues']

                    for item in mouthCues:
                        start = item['start']
                        start_frame = start * FPS
                        current_frame = audio_start_frame + start_frame
                        value = item['value']
                        shape_key_name = value_map[value]
                        # 将timeline设置到current_frame
                        bpy.context.scene.frame_set(int(current_frame))

                        if shape_key_name != 'None':
                            for viseme in all_visemes:
                                if viseme == shape_key_name:
                                    # 将avatar_mesh上的shape_key值设置为1
                                    avatar_mesh.data.shape_keys.key_blocks[viseme].value = 1
                                    # 插入关键帧
                                    avatar_mesh.data.shape_keys.key_blocks[viseme].keyframe_insert(
                                        data_path='value', frame=int(current_frame))
                                else:
                                    avatar_mesh.data.shape_keys.key_blocks[viseme].value = 0
                                    # 插入关键帧
                                    avatar_mesh.data.shape_keys.key_blocks[viseme].keyframe_insert(
                                        data_path='value', frame=int(current_frame))
                        else:
                            for viseme in all_visemes:
                                avatar_mesh.data.shape_keys.key_blocks[viseme].value = 0
                                # 插入关键帧
                                avatar_mesh.data.shape_keys.key_blocks[viseme].keyframe_insert(
                                    data_path='value', frame=int(current_frame))


lip_sync_info_dir = 'g:/fretdance介绍视频音源/视频二'
mesh_name = 'Wolf3D_Avatar'

clear_all_shapekey(mesh_name)
main(lip_sync_info_dir, mesh_name)
