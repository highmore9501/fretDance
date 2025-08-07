import bpy
import json
import mathutils


def clear_all_keyframe(collection_name=None):
    # 选择特定collection下的所有物体
    if collection_name:
        # 取消当前所有选择
        bpy.ops.object.select_all(action='DESELECT')
        # 获取指定collection
        collection = bpy.data.collections.get(collection_name)
        if collection:
            # 选择collection中的所有物体
            for obj in collection.objects:
                obj.select_set(True)
                bpy.context.view_layer.objects.active = obj  # 设置活动对象
        else:
            print(f"Collection '{collection_name}' not found")
            return
    else:
        # 如果没有指定collection，则选择所有物体（原有逻辑）
        bpy.ops.object.select_all(action='SELECT')

    # 清除所有关键帧 - 改进版本
    for ob in bpy.context.selected_objects:
        # 清除对象变换关键帧
        if ob.animation_data:
            if ob.animation_data.action:
                for fcurve in ob.animation_data.action.fcurves:
                    fcurve.keyframe_points.clear()
            # 清除约束关键帧
            for constraint in ob.constraints:
                if constraint.animation_data and constraint.animation_data.action:
                    for fcurve in constraint.animation_data.action.fcurves:
                        fcurve.keyframe_points.clear()

        # 清除形态键关键帧
        if hasattr(ob.data, "shape_keys"):
            if ob.data.shape_keys and ob.data.shape_keys.animation_data:
                if ob.data.shape_keys.animation_data.action:
                    for fcurve in ob.data.shape_keys.animation_data.action.fcurves:
                        fcurve.keyframe_points.clear()

        # 尝试清除所有动画数据
        if ob.animation_data:
            ob.animation_data_clear()
        if hasattr(ob.data, "shape_keys") and ob.data.shape_keys:
            if ob.data.shape_keys.animation_data:
                ob.data.shape_keys.animation_data_clear()

    # 取消全选
    bpy.ops.object.select_all(action='DESELECT')


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

    # 读取json文件
    bpy.context.scene.frame_set(0)  # 从第0帧开始动画，否则会出现插值问题
    for i in range(0, 10):
        current_string = bpy.data.objects.get(f"string{i}", None)
        if current_string is None:
            continue
        # 将current_string上所有的shape_key值设置为0
        for shape_key in current_string.data.shape_keys.key_blocks:
            shape_key.value = 0
            shape_key.keyframe_insert(data_path="value")

    with open(string_recorder, "r") as f:
        stringDicts = json.load(f)

        for item in stringDicts:
            if item["frame"] is None:
                continue
            frame = int(item["frame"])
            stringIndex = item["stringIndex"]
            fret = item["fret"]
            influence = item["influence"]

            # 设置时间
            bpy.context.scene.frame_set(frame)

            current_string = bpy.data.objects[f"string{stringIndex}"]
            if current_string:
                shape_key_name = f's{stringIndex}fret{fret}'
                current_shape_key = current_string.data.shape_keys.key_blocks.get(
                    shape_key_name, None)
                if current_shape_key:
                    # 设置形状关键帧
                    current_shape_key.value = influence
                    current_shape_key.keyframe_insert(data_path="value")
                else:
                    biggest_shape_key_name = f's{stringIndex}fret20'
                    biggest_shape_key = current_string.data.shape_keys.key_blocks[
                        biggest_shape_key_name]
                    if biggest_shape_key:
                        biggest_shape_key.value = influence
                        biggest_shape_key.keyframe_insert(data_path="value")


# 从外部读取json文件
avatar = 'rem'
midi_name = "エケステンドアッシュ-蓬莱人"
track_number = [3]

track_number_string = "_".join([str(track) for track in track_number]) if len(
    track_number) > 1 else str(track_number[0])

left_hand_animation_file = f"G:/fretDance/output/{avatar}_{midi_name}_{track_number_string}_lefthand_animation.json"
right_hand_animation_file = f"G:/fretDance/output/{avatar}_{midi_name}_{track_number_string}_righthand_animation.json"
guitar_string_recorder_file = f"G:/fretDance/output/{midi_name}_{track_number_string}_guitar_string_recorder.json"


clear_all_keyframe()
animate_hand(left_hand_animation_file)
animate_hand(right_hand_animation_file)
animate_string(guitar_string_recorder_file)
