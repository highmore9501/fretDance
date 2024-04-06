import bpy
import json

# 从外部读取json文件

animation = r"G:\fretDance\output\Aguado_12valses_Op1_No2_animation.json"

all_controllers = [
    "R_L", "M_L", "I_L", "P_L",
    "H_L", "HP_L", "H_rotation_Y_L",
    "T_L", "TP_L", "T_rotation_L"
]

all_ik_pivot_bones = ["Thumb_IK_pivot_L"]
armature = "Kamisato IK_arm"

# 读取json文件
with open(animation, "r") as f:
    handDicts = json.load(f)

    for hand in handDicts:
        frame = int(hand["frame"])
        fingerInfos = hand["fingerInfos"]

        # 将blender时间帧设置到frame
        bpy.context.scene.frame_set(frame)

        # 设置每个controller的值
        for controller in all_controllers:
            obj = bpy.data.objects[controller]
            value = fingerInfos[controller]
            if "rotation" in controller:
                obj.rotation_euler = value
                obj.keyframe_insert(data_path="rotation_euler")
            else:
                obj.location = value
                obj.keyframe_insert(data_path="location")

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
