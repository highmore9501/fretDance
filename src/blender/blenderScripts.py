# 一些在blender里跑的工具脚本
import bpy
import mathutils
from blenderRecords import *
from typing import Literal


def clone_deform_bones():
    # 切换到编辑模式
    bpy.ops.object.mode_set(mode='EDIT')

    # 获取当前骨架
    armature = bpy.context.object.data

    # 在编辑模式下复制骨骼
    for bone in bpy.context.selected_bones:
        bone_copy = armature.edit_bones.new("DEF_" + bone.name)
        bone_copy.head = bone.head
        bone_copy.tail = bone.tail
        bone_copy.roll = bone.roll
        bone_copy.parent = bone
        bone_copy.use_deform = True

        # 将骨骼移动到第25层
        bone_copy.layers = [i == 24 for i in range(32)]

    # 切换回姿态模式
    bpy.ops.object.mode_set(mode='POSE')


def move_deform_bones():
    # 切换到pose模式
    bpy.ops.object.mode_set(mode='POSE')

    # 全选所有骨骼
    bpy.ops.pose.select_all(action='SELECT')

    # 移动所有带deform的骨骼到第25层
    for bone in bpy.context.selected_pose_bones:
        if bone.bone.use_deform:
            bone.bone.layers = [i == 24 for i in range(32)]


def remove_empty_vertex_group():
    # 切换到对象模式
    bpy.ops.object.mode_set(mode='OBJECT')

    # 获取当前对象
    obj = bpy.context.object

    # 删除所有没有关联的顶点组
    for vertex_group in obj.vertex_groups:
        group_is_empty = True
        for vertex in obj.data.vertices:
            try:
                vertex_group.weight(vertex.index)
                group_is_empty = False
                break
            except RuntimeError:
                pass
        if group_is_empty:
            obj.vertex_groups.remove(vertex_group)


def remove_non_associated_bones():
    mesh = "Kamisato IK_mesh"
    obj = bpy.data.objects[mesh]
    weight_groups_name = []

    # 获取所有的骨骼组
    for vertex_group in obj.vertex_groups:
        weight_groups_name.append(vertex_group.name)

    armature_name = "Kamisato IK_arm"
    obj = bpy.data.objects[armature_name]

    bpy.ops.object.mode_set(mode='EDIT')

    # 全选所有骨骼
    bpy.ops.armature.select_all(action='SELECT')

    # 遍历所有骨骼，把名字不在weight_groups_name里的骨骼删除
    for bone in bpy.context.selected_bones:
        if bone.name not in weight_groups_name:
            bone.layers = [i == 30 for i in range(32)]

    # 切换回姿态模式
    bpy.ops.object.mode_set(mode='POSE')


def read_vertex_groups():
    mesh = "Kamisato IK_mesh"
    obj = bpy.data.objects[mesh]
    weight_groups_R = []
    weight_groups_L = []

    # 获取所有的骨骼组
    for vertex_group in obj.vertex_groups:
        if vertex_group.name.endswith("_R"):
            weight_groups_R.append(vertex_group.name)
        elif vertex_group.name.endswith("_L"):
            weight_groups_L.append(vertex_group.name)

    return weight_groups_R, weight_groups_L


def compare_LR_groups():
    right, left = read_vertex_groups()
    remap_R = []
    for item in right:
        item = item[:-2]
        remap_R.append(item)

    remap_L = []
    for item in left:
        item = item[:-2]
        remap_L.append(item)

    # 比较两个列表的差异
    diff = list(set(remap_R).difference(set(remap_L)))
    print(diff)


def export_controller_info(isLeftHand: bool = True):
    collections = ['PositionControllers',
                   'RotationControllers', 'PivotControllers', 'RightFingerVector']

    armature = "Kamisato IK_arm"
    base_bone_name = "cf_s_spine03"
    base_bone = bpy.data.objects[armature].pose.bones[base_bone_name]
    base_bone_matrix = base_bone.matrix
    invert_base_bone_matrix = base_bone_matrix.inverted()

    result = {}

    for collection in collections:
        # 遍历所有collection里的的物体
        for obj in bpy.data.collections[collection].objects:
            obj_name = obj.name
            if (isLeftHand and obj_name.endswith("_L")) or (not isLeftHand and obj_name.endswith("_R")):
                try:
                    if collection != "RotationControllers" and collection != 'RightFingerVector':
                        # 位置控制器
                        obj_info = obj.location
                        obj_info = invert_base_bone_matrix @ obj_info
                        result[obj_name] = [obj_info.x, obj_info.y, obj_info.z]
                    else:
                        # 旋转控制器
                        obj_info = obj.rotation_euler
                        obj_info = invert_base_bone_matrix @ obj_info
                        result[obj_name] = [obj_info.x, obj_info.y, obj_info.z]
                except:
                    pass

    print(result)


def import_controller_info(position_name: str, status_name: Literal["normal", "outer", "inner"]):
    collections = ['FingerPositionControllers',
                   'RotationControllers', 'HandPositionControllers']

    armature = "Kamisato IK_arm"
    base_bone_name = "cf_s_spine03"

    base_bone = bpy.data.objects[armature].pose.bones[base_bone_name]
    base_bone_matrix = base_bone.matrix

    hand_position_dict = NORMAL_LEFT_HAND_POSITIONS if status_name == "normal" else (
        OUTER_LEFT_HAND_POSITIONS if status_name == "outer" else INNER_LEFT_HAND_POSITIONS)
    hand_rotation_dict = NORMAL_LEFT_HAND_ROTATIONS if status_name == "normal" else (
        OUTER_LEFT_HAND_ROTATIONS if status_name == "outer" else INNER_LEFT_HAND_ROTATIONS)

    for collection in collections:
        for obj in bpy.data.collections[collection].objects:
            obj_name = obj.name
            if obj_name.endswith("_R"):
                continue
            try:
                if collection == "PositionControllers" and not (obj_name.startswith("T") or obj_name.startswith("P")):
                    obj.location = base_bone_matrix @ mathutils.Vector(
                        LEFT_FINGER_POSITIONS[position_name])
                elif collection == "PositionControllers":
                    obj.location = base_bone_matrix @ mathutils.Vector(
                        hand_position_dict[position_name][obj_name])
                elif collection == "RotationControllers":
                    obj.rotation_euler = mathutils.Euler(
                        hand_rotation_dict[position_name][obj_name])
            except:
                pass


def export_positions(collection: str, armature_name: str, bone_name: str):
    armature = bpy.data.objects[armature_name]
    bone = armature.pose.bones[bone_name]
    bone_matrix_inv = bone.matrix.inverted()
    result = {}
    for obj in bpy.data.collections[collection].objects:
        obj_name = obj.name
        obj_info = bone_matrix_inv @ obj.matrix_world.to_translation()
        result[obj_name] = {
            "position": [obj_info.x, obj_info.y, obj_info.z],
        }
    print(result)


def export_local_positions(obj, armature_name: str, bone_name: str):
    import numpy as np
    armature = bpy.data.objects[armature_name]
    bone = armature.pose.bones[bone_name]
    result = {}
    for key, value in obj.items():
        if key in ['H_L', 'HP_L',  'T_L', 'TP_L']:
            position = np.array(value['position'])
            # 将位置向量转换到骨骼的本地坐标系
            local_position = bone.matrix.inverted() @ mathutils.Vector(position)
            # 更新位置值
            result[key] = [local_position.x,
                           local_position.y, local_position.z]
    print(result)


def export_directions(collection: str, armature_name: str, bone_name: str):
    armature = bpy.data.objects[armature_name]
    bone = armature.pose.bones[bone_name]
    bone_matrix_inv = bone.matrix.inverted()
    result = {}
    for obj in bpy.data.collections[collection].objects:
        obj_name = obj.name
        rotation_vector = mathutils.Vector((0, 0, 1))  # Z-axis vector
        rotation_vector.rotate(obj.rotation_euler)
        unit_vector = rotation_vector.normalized()
        if not obj_name.startswith('T'):
            unit_vector = -unit_vector
        # Transform the direction vector to the bone's local coordinate system
        local_direction = bone_matrix_inv.to_3x3() @ unit_vector
        result[obj_name] = {
            "direction": [local_direction.x, local_direction.y, local_direction.z],
        }
    print(result)


def animateObject(obj, prefix):
    for i in range(6):
        key = prefix + str(i)
        target_obj = bpy.data.objects.get(key)
        if target_obj:
            bpy.context.scene.frame_set(i*5)
            # Convert the target object's location to world coordinates
            world_location = target_obj.matrix_world.to_translation()
            obj.location = world_location
            obj.keyframe_insert(data_path="location")


def animateRightHandTest():
    collection_name = "PositionControllers"

    for obj in bpy.data.collections[collection_name].objects:
        obj_name = obj.name
        if not obj_name.endswith("_R"):
            continue
        if obj_name.startswith("I"):
            animateObject(obj, 'i')
        elif obj_name.startswith("M"):
            animateObject(obj, 'm')
        elif obj_name.startswith("R"):
            animateObject(obj, 'a')
        elif obj_name.startswith("P"):
            animateObject(obj, 'ch')
        elif obj_name.startswith("T"):
            animateObject(obj, 'p')


def caculateLocalPosition(obj_name: str, armature: str, target_bone: str):
    # 获取骨骼对象
    bone = bpy.data.objects[armature].pose.bones[target_bone]

    # 获取对象
    obj = bpy.data.objects[obj_name]

    # 计算对象在骨骼的坐标系里的location
    position = bone.matrix.inverted() @ obj.location
    print(position)


def add_random_rotation():
    import random
    import bpy
    import mathutils

    # 获取所有选中的骨骼
    selected_bones = bpy.context.selected_pose_bones_from_active_object

    for pose_bone in selected_bones:
        # 设置当前激活的对象和骨骼
        pose_bone.rotation_mode = 'XYZ'

        pose_bone.rotation_euler = mathutils.Euler(
            [random.random()*0.05, random.random()*0.05, random.random()*0.05])


if __name__ == "__main__":
    pass
