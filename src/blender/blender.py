import bpy
import json
import mathutils

# 从外部读取json文件
avatar = 'rem'
midi_name = "Corridors Of Time Fingerstyle"
track_number = 1

left_hand_animation_file = f"G:/fretDance/output/{avatar}_{midi_name}_{track_number}_lefthand_animation.json"
right_hand_animation_file = f"G:/fretDance/output/{avatar}_{midi_name}_{track_number}_righthand_animation.json"
guitar_string_recorder_file = f"output/{midi_name}_{track_number}_guitar_string_recorder.json"


def animate_hand(animation_file: str):
    # 读取json文件
    with open(animation_file, "r") as f:
        handDicts = json.load(f)

        # 将所有的帧存储在一个列表中
        frames = [int(hand["frame"]) for hand in handDicts]

        for i in range(len(frames)):
            frame = frames[i]
            fingerInfos = handDicts[i]["fingerInfos"]

            # 将blender时间帧设置到frame
            bpy.context.scene.frame_set(frame)
            insert_values(fingerInfos)


def insert_values(fingerInfos):
    # 设置每个controller的值
    for fingerInfo in fingerInfos:
        try:
            obj = bpy.data.objects[fingerInfo]
            value = fingerInfos[fingerInfo]
            if "rotation" in fingerInfo:
                obj.rotation_euler = value
                obj.keyframe_insert(data_path="rotation_euler")
            else:
                value = mathutils.Vector(value)
                obj.location = value
                obj.keyframe_insert(data_path="location")
        except:
            pass


def animate_string(string_recorder: str):
    biggest_shape_key_name = 'fret20'
    # 读取json文件
    bpy.context.scene.frame_set(0)  # 从第0帧开始动画，否则会出现插值问题
    for i in range(0, 6):
        current_string = bpy.data.objects[f"string{i}"]
        # 将current_string上所有的shape_key值设置为0
        for shape_key in current_string.data.shape_keys.key_blocks:
            shape_key.value = 0
            shape_key.keyframe_insert(data_path="value")

    with open(string_recorder, "r") as f:
        stringDicts = json.load(f)

        for item in stringDicts:
            frame = int(item["frame"])
            stringIndex = item["stringIndex"]
            fret = item["fret"]
            influence = item["influence"]

            # 设置时间
            bpy.context.scene.frame_set(frame)

            current_string = bpy.data.objects[f"string{stringIndex}"]
            if current_string:
                shape_key_name = f'fret{fret}'
                current_shape_key = current_string.data.shape_keys.key_blocks[shape_key_name]
                if current_shape_key:
                    # 设置形状关键帧
                    current_shape_key.value = influence
                    current_shape_key.keyframe_insert(data_path="value")
                else:
                    biggest_shape_key = current_string.data.shape_keys.key_blocks[
                        biggest_shape_key_name]
                    if biggest_shape_key:
                        biggest_shape_key.value = influence
                        biggest_shape_key.keyframe_insert(data_path="value")


animate_hand(left_hand_animation_file)
animate_hand(right_hand_animation_file)
animate_string(guitar_string_recorder_file)
