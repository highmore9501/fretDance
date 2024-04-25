import bpy
import json
import mathutils

# 从外部读取json文件

left_hand_animation = r"G:\fretDance\output\Corridors Of Time Fingerstyle_lefthand_animation.json"
right_hand_animation = r"G:\fretDance\output\Corridors Of Time Fingerstyle_righthand_animation.json"

armature = "Kamisato IK_arm"
base_bone_name = "cf_s_spine03"


def animate_hand(animation_file: str):
    # 先计算base_bone的矩阵
    base_bone = bpy.data.objects[armature].pose.bones[base_bone_name]
    base_bone_matrix = base_bone.matrix

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
            insert_values(fingerInfos, base_bone_matrix)

            # 如果当前帧和下一帧的差值大于3，则在两帧之间插入额外的帧
            if i < len(frames) - 1 and frames[i + 1] - frame > 3:
                for extra_frame in range(frame + 1, frames[i + 1]):
                    bpy.context.scene.frame_set(extra_frame)
                    insert_values(fingerInfos, base_bone_matrix)


def insert_values(fingerInfos, base_bone_matrix):
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


animate_hand(left_hand_animation)
animate_hand(right_hand_animation)
