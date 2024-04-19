import bpy
import json
import mathutils
import math

# 从外部读取json文件

left_hand_animation = r"G:\fretDance\output\Corridors Of Time Fingerstyle_lefthand_animation.json"
right_hand_animation = r"G:\fretDance\output\Corridors Of Time Fingerstyle_righthand_animation.json"

left_finger_bones = ["DEF_IndexFinger3_L",
                     "DEF_MiddleFinger3_L",
                     "DEF_RingFinger3_L",
                     "DEF_LittleFinger3_L",]
right_finger_bones = ["DEF_IndexFinger3_R",
                      "DEF_MiddleFinger3_R",
                      "DEF_RingFinger3_R",
                      "DEF_LittleFinger3_R", "DEF_Thumb2_R"]
armature = "Kamisato IK_arm"

rolls = {}

# 选中armature
bpy.context.view_layer.objects.active = bpy.data.objects[armature]
# edit mode
bpy.ops.object.mode_set(mode='EDIT')

# 遍历所有骨骼
for bone in bpy.context.object.data.edit_bones:
    if bone.name in left_finger_bones or bone.name in right_finger_bones:
        rolls[bone.name] = bone.roll


# 切换回object模式
bpy.ops.object.mode_set(mode='OBJECT')


def animate_left_hand(left_hand_animation: str):
    FretBoardNormal = get_vector_from_obj("FretBoardNormal")
    LeftThumbDirection = get_vector_from_obj("LeftThumbDirection")
    current_H_L = pre_H_L = mathutils.Vector((0, 0, 0))
    angels = {}
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
                    if fingerInfo == "H_L":
                        current_H_L = mathutils.Vector(
                            (value[0], value[1], value[2]))
                except:
                    pass

            # 选中armature
            bpy.context.view_layer.objects.active = bpy.data.objects[armature]
            # 切换到pose mode
            bpy.ops.object.mode_set(mode='POSE')

            for bone in bpy.context.object.pose.bones:
                bone_name = bone.name
                if bone_name in left_finger_bones:
                    if "Thumb" in bone_name:
                        direction = LeftThumbDirection
                    else:
                        direction = FretBoardNormal
                    start_bone_name = bone_name.replace("3", "1")
                    start_bone_name = start_bone_name.replace("2", "1")
                    start_bone_name = start_bone_name.replace("DEF_", "")
                    end_bone_name = bone_name.replace("DEF_", "")
                    angel = rotate_finger_angle_by_normal(
                        start_bone_name, end_bone_name, direction)
                    bone.rotation_euler[1] = angel
                    angels[bone_name] = bone.rotation_euler[1]
                    bone.keyframe_insert(data_path="rotation_euler")

            # 切换到object mode
            bpy.ops.object.mode_set(mode='OBJECT')


def animate_right_hand(left_hand_animation: str):
    FretBoardNormal = get_vector_from_obj("FretBoardNormal")
    RightThumbDirection = get_vector_from_obj("RightThumbDirection")
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
                if bone_name in left_finger_bones:
                    if "Thumb" in bone_name:
                        direction = RightThumbDirection
                    else:
                        direction = FretBoardNormal
                    start_bone_name = bone_name.replace("3", "1")
                    start_bone_name = start_bone_name.replace("2", "1")
                    angel = rotate_finger_angle_by_normal(
                        start_bone_name, bone_name, direction)
                    bone.rotation_euler[1] += angel
                    bone.keyframe_insert(data_path="rotation_euler")

            # 切换到object mode
            bpy.ops.object.mode_set(mode='OBJECT')


def rotate_finger_angle_by_normal(start_bone_name: str, end_bone_name: str, normal: mathutils.Vector) -> float:

    # 获取骨骼对象
    start_bone = bpy.context.active_object.pose.bones[start_bone_name]
    end_bone = bpy.context.active_object.pose.bones[end_bone_name]

    # 读取start_bone的世界坐标到end_bone的世界坐标的向量
    vector1 = start_bone.matrix.to_translation(
    ) - end_bone.matrix.to_translation()

    # 将vector1转换到end_bone的坐标系中
    vector1 = end_bone.matrix.inverted().to_quaternion() @ vector1
    # vector2就是Y轴
    vector2 = mathutils.Vector((0, 1, 0))

    Normal_Y = vector1.cross(vector2)  # 平面的法向量

    # 计算Normal_Y在XZ平面上的二维向量
    Normal_Y_2d = mathutils.Vector((Normal_Y.x, Normal_Y.z))
    Normal_Y_2d.normalize()

    # 计算此时的Z轴在xz平面上的二维向量与Normal_Y_2d的旋转值
    angle = mathutils.Vector((0, -1)).angle_signed(Normal_Y_2d)

    if angle > math.pi/2:
        angle = angle - math.pi
    if angle < -math.pi/2:
        angle = angle + math.pi

    # 返回夹角的弧度值
    return angle


def get_position_by_normal(finger_name: str, normal: mathutils.Vector) -> mathutils.Vector:
    # 获取骨骼对象
    bone = bpy.context.active_object.pose.bones[finger_name]

    # 读取Bone的世界坐标
    bone_world = bone.matrix.to_translation()

    # 计算从Bone的世界坐标往normal方向移动10个单位以后的位置
    position = bone_world + 10 * normal

    return position


def get_vector_from_obj(obj_name: str) -> mathutils.Vector:
    obj = bpy.data.objects[obj_name]
    return obj.matrix_world.to_quaternion() @ mathutils.Vector((0, 0, 1))


animate_left_hand(left_hand_animation)
# animate_right_hand(right_hand_animation)
