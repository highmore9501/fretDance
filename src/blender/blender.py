import bpy
import json
import mathutils
import math

# 从外部读取json文件

left_hand_animation = r"G:\fretDance\output\Corridors Of Time Fingerstyle_lefthand_animation.json"
right_hand_animation = r"G:\fretDance\output\Corridors Of Time Fingerstyle_righthand_animation.json"

armature = "Kamisato IK_arm"
base_bone_name = "cf_s_spine03"


def animate_left_hand(left_hand_animation: str):
    # 先计算base_bone的矩阵
    base_bone = bpy.data.objects[armature].pose.bones[base_bone_name]
    base_bone_matrix = base_bone.matrix

    # 读取json文件
    with open(left_hand_animation, "r") as f:
        handDicts = json.load(f)

        for hand in handDicts:
            frame = int(hand["frame"])
            fingerInfos = hand["fingerInfos"]

            # 将blender时间帧设置到frame
            bpy.context.scene.frame_set(frame)

            # 设置每个controller的值
            for fingerInfo in fingerInfos:
                try:
                    obj = bpy.data.objects[fingerInfo]
                    value = fingerInfos[fingerInfo]
                    if "rotation" in fingerInfo:
                        obj.rotation_euler = value
                        obj.keyframe_insert(data_path="rotation_euler")
                    else:
                        # 把value从base_bone的坐标系转换到世界坐标系
                        value = base_bone_matrix @ mathutils.Vector(value)
                        obj.location = value
                        obj.keyframe_insert(data_path="location")
                except:
                    pass


def animate_right_hand(right_hand_animation: str):
    # 读取json文件
    with open(right_hand_animation, "r") as f:
        handDicts = json.load(f)

        for hand in handDicts:
            frame = int(hand["frame"])
            fingerInfos = hand["fingerInfos"]

            # 将blender时间帧设置到frame
            bpy.context.scene.frame_set(frame)

            # 设置每个controller的值
            for fingerInfo in fingerInfos:
                try:
                    obj = bpy.data.objects[fingerInfo]
                    value = fingerInfos[fingerInfo]
                    obj.location = value
                    obj.keyframe_insert(data_path="location")
                except:
                    pass


animate_left_hand(left_hand_animation)
animate_right_hand(right_hand_animation)
