import bpy  # type: ignore
import json
import mathutils


def collect_collection_objects(col, exclude_names, object_names):
    # 收集当前collection中的所有物体名称
    for obj in col.objects:
        # 检查物体是否在排除列表中
        if obj.name in exclude_names:
            print(f"Excluding object: {obj.name}")
            continue
        object_names.append(obj.name)
        print(f"Collected object: {obj.name}")  # 调试语句

    # 递归处理所有子collection
    for child_col in col.children:
        # 检查子集合是否在排除列表中
        if child_col.name in exclude_names:
            print(f"Excluding collection: {child_col.name}")
            continue
        collect_collection_objects(child_col, exclude_names, object_names)


def clear_all_keyframe(collection_name=None, exclude_names=None):
    """
    清除关键帧函数

    Args:
        collection_name: 要处理的集合名称
        exclude_names: 要排除的物体名称或集合名称列表
    """
    if exclude_names is None:
        exclude_names = []

    # 收集特定collection下的所有物体名称
    object_names = []
    if collection_name:
        # 获取指定collection
        collection = bpy.data.collections.get(collection_name)
        if collection:
            # 递归收集collection及其所有子collection中的物体名称
            collect_collection_objects(collection, exclude_names, object_names)
            # 调试语句
            print(f"Total collected objects: {len(object_names)}")
        else:
            print(f"Collection '{collection_name}' not found")
            return
    else:
        # 如果没有指定collection，则收集所有物体（排除列表中的除外）
        for obj in bpy.data.objects:
            if obj.name not in exclude_names:
                object_names.append(obj.name)
                print(f"Collected object: {obj.name}")

    # 清除所有关键帧 - 改进版本
    # 调试语句
    print(f"Processing {len(object_names)} objects for animation clearing")

    for obj_name in object_names:
        # 通过名称获取物体对象
        ob = bpy.data.objects.get(obj_name)
        if ob is None:
            print(f"Warning: Object {obj_name} not found")
            continue

        # 额外检查：确保物体不在排除列表中
        if ob.name in exclude_names:
            print(f"Skipping excluded object: {ob.name}")
            continue

        print(f"Processing object: {ob.name}")  # 调试语句

        # 特殊处理以"Tar"开头的对象
        if ob.name.startswith("Tar"):
            # 对于以Tar开头的物体，只清除Z轴动画数据
            print(
                f"Clearing only Z-axis animation for target object: {ob.name}")
            if ob.animation_data and ob.animation_data.action:
                # 删除Z轴(location[2])的关键帧
                fcurves_to_remove = []
                for fcurve in ob.animation_data.action.fcurves:
                    if fcurve.data_path == "location" and fcurve.array_index == 2:
                        fcurve.keyframe_points.clear()
                        # 如果这条fcurve已经没有关键帧，标记为待删除
                        if len(fcurve.keyframe_points) == 0:
                            fcurves_to_remove.append(fcurve)

                # 删除空的fcurve（可选）
                for fcurve in fcurves_to_remove:
                    ob.animation_data.action.fcurves.remove(fcurve)

            # 处理形态键（如果有的话）
            if hasattr(ob.data, "shape_keys") and ob.data.shape_keys:
                # 首先归零所有shape key的值
                for shape_key_block in ob.data.shape_keys.key_blocks:
                    shape_key_block.value = 0.0
                    print(f"Reset shape key {shape_key_block.name} to 0.0")

                # 然后清除形态键动画数据
                if ob.data.shape_keys.animation_data:
                    print(
                        f"Object {ob.name} has shape keys with animation data")
                    if ob.data.shape_keys.animation_data.action:
                        for fcurve in ob.data.shape_keys.animation_data.action.fcurves:
                            print(
                                f"Clearing {len(fcurve.keyframe_points)} shape key keyframes from {ob.name}")
                            fcurve.keyframe_points.clear()
                    # 清除形态键动画数据
                    ob.data.shape_keys.animation_data_clear()

            # 处理完Tar对象后直接跳到下一个对象
            continue

        # 清除对象变换关键帧（仅针对非Tar对象）
        if ob.animation_data:
            print(f"Object {ob.name} has animation_data")  # 调试语句
            if ob.animation_data.action:
                # 调试语句
                print(
                    f"Object {ob.name} has action with {len(ob.animation_data.action.fcurves)} fcurves")
                for fcurve in ob.animation_data.action.fcurves:
                    # 调试语句
                    print(
                        f"Clearing {len(fcurve.keyframe_points)} keyframes from {ob.name}")
                    fcurve.keyframe_points.clear()

         # 清除形态键关键帧并归零形态键值
        if hasattr(ob.data, "shape_keys"):
            if ob.data.shape_keys:
                # 首先归零所有shape key的值
                for shape_key_block in ob.data.shape_keys.key_blocks:
                    shape_key_block.value = 0.0
                    print(f"Reset shape key {shape_key_block.name} to 0.0")

                # 然后清除形态键动画数据
                if ob.data.shape_keys.animation_data:
                    # 调试语句
                    print(
                        f"Object {ob.name} has shape keys with animation data")
                    if ob.data.shape_keys.animation_data.action:
                        for fcurve in ob.data.shape_keys.animation_data.action.fcurves:
                            # 调试语句
                            print(
                                f"Clearing {len(fcurve.keyframe_points)} shape key keyframes from {ob.name}")
                            fcurve.keyframe_points.clear()

        # 尝试清除所有动画数据
        if ob.animation_data:
            print(f"Clearing animation data for {ob.name}")  # 调试语句
            ob.animation_data_clear()
        if hasattr(ob.data, "shape_keys") and ob.data.shape_keys:
            if ob.data.shape_keys.animation_data:
                # 调试语句
                print(f"Clearing shape key animation data for {ob.name}")
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
                # 检查value是欧拉角(3个元素)还是四元数(4个元素)
                if len(value) == 4:
                    # 四元数模式
                    obj.rotation_mode = 'QUATERNION'
                    obj.rotation_quaternion = value
                    obj.keyframe_insert(data_path="rotation_quaternion")
                else:
                    # 欧拉角模式，但不用考虑具体是哪一种，因为不同文件中可能使用了不同的模式
                    obj.rotation_euler = value
                    obj.keyframe_insert(data_path="rotation_euler")
            else:
                value = mathutils.Vector(value)
                obj.location = value
                obj.keyframe_insert(data_path="location")
        except:
            pass


def animate_string(string_recorder: str):
    guitar_name = 'guitar'
    guitar_obj = bpy.data.objects.get(guitar_name, None)

    # 判断模型类型：分离式（弦和吉他分开）还是合并式（弦和吉他合并）
    model_type = "merged"  # 默认为合并式
    separate_strings = {}  # 存储分离的弦对象

    # 检查是否存在独立的弦对象
    for i in range(0, 10):
        string_obj = bpy.data.objects.get(f"string{i}", None)
        if string_obj and string_obj != guitar_obj and string_obj.data.shape_keys:
            separate_strings[i] = string_obj
            model_type = "separate"  # 如果找到独立弦对象，则为分离式

    # 读取json文件
    bpy.context.scene.frame_set(0)  # 从第0帧开始动画，否则会出现插值问题

    # 根据模型类型初始化shape key值
    if model_type == "separate":
        # 分离式：处理独立的弦对象
        for string_index, string_obj in separate_strings.items():
            for shape_key in string_obj.data.shape_keys.key_blocks:
                shape_key.value = 0
                shape_key.keyframe_insert(data_path="value")
    else:
        # 合并式：处理吉他对象上的shape key
        if guitar_obj and guitar_obj.data.shape_keys:
            for shape_key in guitar_obj.data.shape_keys.key_blocks:
                shape_key.value = 0
                shape_key.keyframe_insert(data_path="value")

    print("model_type:", model_type)

    with open(string_recorder, "r") as f:
        stringDicts = json.load(f)

        steps = len(stringDicts)

        for i in range(steps):
            item = stringDicts[i]
            if item["frame"] is None:
                continue

            if i % 100 == 0:  # 每隔100步打印一次进度
                print(f"processing step {i}/{steps}")

            frame = int(item["frame"])
            stringIndex = item["stringIndex"]
            fret = item["fret"]
            influence = item["influence"]

            # 设置时间
            bpy.context.scene.frame_set(frame)

            if model_type == "separate":
                # 分离式模型处理
                current_string = separate_strings.get(stringIndex, None)
            else:
                # 合并式模型处理
                current_string = guitar_obj

            if current_string:
                # 新增功能：检查并设置自定义属性"is_vib"
                if "is_vib" in current_string:
                    current_string["is_vib"] = influence
                    current_string.keyframe_insert(data_path='["is_vib"]')

                shape_key_name = f's{stringIndex}fret{fret}'
                current_shape_key = current_string.data.shape_keys.key_blocks.get(
                    shape_key_name, None) if current_string.data.shape_keys else None

                if current_shape_key:
                    # 设置形状关键帧
                    current_shape_key.value = influence
                    current_shape_key.keyframe_insert(data_path="value")
                else:
                    biggest_shape_key_name = f's{stringIndex}fret20'
                    if current_string.data.shape_keys:
                        biggest_shape_key = current_string.data.shape_keys.key_blocks.get(
                            biggest_shape_key_name, None)
                        if biggest_shape_key:
                            biggest_shape_key.value = influence
                            biggest_shape_key.keyframe_insert(
                                data_path="value")


# 从外部读取json文件
avatar = '神里绫华-花时来信'
midi_name = "妖怪之山"
track_number = [2, 5]

track_number_string = "_".join([str(track) for track in track_number]) if len(
    track_number) > 1 else str(track_number[0])

left_hand_animation_file = f"G:/fretDance/output/hand_animation/{avatar}_{midi_name}_{track_number_string}_lefthand_animation.json"
right_hand_animation_file = f"G:/fretDance/output/hand_animation/{avatar}_{midi_name}_{track_number_string}_righthand_animation.json"
guitar_string_recorder_file = f"G:/fretDance/output/string_recorder/{midi_name}_{track_number_string}_guitar_string_recorder.json"


clear_all_keyframe()
animate_hand(left_hand_animation_file)
animate_hand(right_hand_animation_file)
animate_string(guitar_string_recorder_file)
