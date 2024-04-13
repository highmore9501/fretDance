import bpy
import json

# 从外部读取json文件

left_hand_animation = r"G:\fretDance\output\Corridors Of Time Fingerstyle_lefthand_animation.json"
right_hand_animation = r"G:\fretDance\output\Corridors Of Time Fingerstyle_righthand_animation.json"

all_ik_pivot_bones = ["Thumb_IK_pivot_L"]
armature = "Kamisato IK_arm"


def animate_left_hand(left_hand_animation: str):
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
                        obj.location = value
                        obj.keyframe_insert(data_path="location")
                except:
                    pass

            # 选中armature
            bpy.context.view_layer.objects.active = bpy.data.objects[armature]
            # 切换到pose mode
            bpy.ops.object.mode_set(mode='POSE')
            # 遍历所有骨骼
            for bone in bpy.context.object.pose.bones:
                bone_name = bone.name
                if bone_name in all_ik_pivot_bones:
                    bone.location = fingerInfos[bone_name]
                    bone.keyframe_insert(data_path="location")
            # 切换到object mode
            bpy.ops.object.mode_set(mode='OBJECT')


def animate_right_hand(left_hand_animation: str):
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
                        obj.location = value
                        obj.keyframe_insert(data_path="location")
                except:
                    pass


animate_left_hand(left_hand_animation)
animate_right_hand(right_hand_animation)
