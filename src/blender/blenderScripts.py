# 一些在blender里跑的工具脚本
import bpy
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
    """
    useage:这个方法用于在blender中将所有的deform骨骼移动到第25层
    """
    # 切换到pose模式
    bpy.ops.object.mode_set(mode='POSE')

    # 全选所有骨骼
    bpy.ops.pose.select_all(action='SELECT')

    # 移动所有带deform的骨骼到第25层
    for bone in bpy.context.selected_pose_bones:
        if bone.bone.use_deform:
            bone.bone.layers = [i == 24 for i in range(32)]


def remove_empty_vertex_group():
    """
    useage:这个方法用于在blender中删除没有关联的顶点组
    """
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


def remove_non_associated_bones(mesh_name: str, armature_name: str):
    """
    :param mesh_name: 网格名称
    :param armature_name: 骨骼名称
    useage:这个方法用于在blender中删除没有关联的骨骼。注意这个方法非常危险，执行前要想明白自己在做什么
    """

    obj = bpy.data.objects[mesh_name]
    weight_groups_name = []

    # 获取所有的骨骼组
    for vertex_group in obj.vertex_groups:
        weight_groups_name.append(vertex_group.name)

    obj = bpy.data.objects[armature_name]

    bpy.ops.object.mode_set(mode='EDIT')

    # 全选所有骨骼
    bpy.ops.armature.select_all(action='SELECT')

    # 遍历所有骨骼，把名字不在weight_groups_name里的骨骼删除
    for bone in bpy.context.selected_bones:
        if bone.name not in weight_groups_name:
            # 删除骨骼
            bpy.ops.armature.delete()

    # 切换回姿态模式
    bpy.ops.object.mode_set(mode='POSE')


def read_vertex_groups(mesh: str):
    """
    :param mesh: 网格名称
    useage:这个方法用于在blender中读取左右两边的权重组
    """
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
    """
    useage:这个方法用于在blender中比较左右两边的权重组的差异
    """
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


def find_non_associated_groups(armature_name: str, mesh_name: str):
    """    
    :param armature_name: 骨骼名称
    :param mesh_name: 网格名称
    useage:这个方法用于在blender中找到没有关联骨骼的权重组
    """
    armature = bpy.data.objects[armature_name]
    # 获取所有的骨骼组
    bones = []
    for bone in armature.pose.bones:
        bones.append(bone.name)

    mesh = bpy.data.objects[mesh_name]
    non_associated_groups = []
    for vertex_group in mesh.vertex_groups:
        if vertex_group.name not in bones:
            non_associated_groups.append(vertex_group.name)
    print(non_associated_groups)


def import_left_controller_info(position_name: Literal["P0", "P1", "P2", "P3"], status_name: Literal["Normal", "Outer", "Inner"]):
    """    
    :param position_name: 位置名称
    :param status_name: 状态名称
    useage:这个方法用于在blender中快速将人物左手放置成某个特定的状态。这几个状态分别是，Noraml情况下的P0-P3，Outer情况下的P0和P2，Inner情况下的P1和P3
    """
    collections = ['FingerPositionControllers',
                   'RotationControllers', 'HandPositionControllers']

    for collection in collections:
        for obj in bpy.data.collections[collection].objects:
            obj_name = obj.name
            if obj_name.endswith("_R"):
                continue
            try:
                if collection == "HandPositionControllers":
                    position_ball_name = f'{status_name}_{position_name}_{obj_name}'
                    obj.location = bpy.data.objects[position_ball_name].location
                elif collection == "FingerPositionControllers":
                    position_ball_name = f'Fret_{position_name}'
                    obj.location = bpy.data.objects[position_ball_name].location
                elif collection == "RotationControllers":
                    rotation_cone_name = f'{status_name}_{position_name}_H_rotation_L'
                    obj.rotation_euler = bpy.data.objects[rotation_cone_name].rotation_euler
            except Exception as e:
                print(f"Error: {e}")


def set_left_controller_info_to_position_balls(position_name: Literal["P0", "P1", "P2", "P3"], status_name: Literal["Normal", "Outer", "Inner"]):
    """    
    :param position_name: 位置名称
    :param status_name: 状态名称
    useage:这个方法同import_left_controller_info，但是是将球的位置设置到控制器上
    """
    collections = ['FingerPositionControllers',
                   'RotationControllers', 'HandPositionControllers']

    for collection in collections:
        for obj in bpy.data.collections[collection].objects:
            obj_name = obj.name
            if obj_name.endswith("_R"):
                continue
            try:
                if collection == "HandPositionControllers":
                    position_ball_name = f'{status_name}_{position_name}_{obj_name}'
                    bpy.data.objects[position_ball_name].location = obj.location
                elif collection == "FingerPositionControllers":
                    position_ball_name = f'Fret_{position_name}'
                    if obj.name == 'I_L':
                        bpy.data.objects[position_ball_name].location = obj.location
                elif collection == "RotationControllers":
                    rotation_cone_name = f'{status_name}_{position_name}_H_rotation_L'
                    bpy.data.objects[rotation_cone_name].rotation_euler = obj.rotation_euler
            except Exception as e:
                print(f"Error: {e}")


def import_right_controller_info(hand_position: int):
    """
    useage:这个方法用于在blender中快速将人物右手放置成某个特定的状态。方便进行下一步的微调
    """
    collection = 'FingerPositionControllers'
    right_hand_test_positions = {
        0: {"p": 2, "i": 0, "m": 0, "a": 0},
        1: {"p": 3, "i": 1, "m": 1, "a": 0},
        2: {"p": 5, "i": 2, "m": 1, "a": 0},
        3: {"p": 5, "i": 4, "m": 3, "a": 2},
        4: {"p": '_end', "i": '_end', "m": '_end', "a": '_end'}
    }

    finger_positions = right_hand_test_positions[hand_position]

    # 设置右手位置
    hand_position_name = f'h{hand_position}' if hand_position != 4 else 'h_end'
    H_R = bpy.data.objects['H_R']
    H_R.location = bpy.data.objects[hand_position_name].location

    # 设置大拇指位置
    thumb_position_name = f'p{finger_positions["p"]}'
    T_R = bpy.data.objects['T_R']
    T_R.location = bpy.data.objects[thumb_position_name].location

    for obj in bpy.data.collections[collection].objects:
        obj_name = obj.name
        if obj_name.endswith("_L"):
            continue
        try:
            if obj_name.startswith("I"):
                position_ball_name = f'i{finger_positions["i"]}'
            elif obj_name.startswith("M"):
                position_ball_name = f'm{finger_positions["m"]}'
            elif obj_name.startswith("R"):
                position_ball_name = f'a{finger_positions["a"]}'
            elif obj_name.startswith("P"):
                position_ball_name = f'ch{finger_positions["a"]}'
            else:
                print(f'Error happend. name: {obj_name}')
            obj.location = bpy.data.objects[position_ball_name].location

        except Exception as e:
            print(f"Error: {e}")


def set_right_controller_info_to_position_balls(hand_position: int):
    """
    useage:这个方法同import_right_controller_info，但是是将球的位置设置到控制器上
    """
    collection = 'FingerPositionControllers'
    right_hand_test_positions = {
        0: {"p": 2, "i": 0, "m": 0, "a": 0},
        1: {"p": 3, "i": 1, "m": 1, "a": 0},
        2: {"p": 5, "i": 2, "m": 1, "a": 0},
        3: {"p": 5, "i": 4, "m": 3, "a": 2},
        4: {"p": '_end', "i": '_end', "m": '_end', "a": '_end'}
    }

    finger_positions = right_hand_test_positions[hand_position]

    # 设置右手位置
    hand_position_name = f'h{hand_position}' if hand_position != 4 else 'h_end'
    H_R = bpy.data.objects['H_R']
    bpy.data.objects[hand_position_name].location = H_R.location

    # 设置大拇指位置
    thumb_position_name = f'p{finger_positions["p"]}'
    T_R = bpy.data.objects['T_R']
    bpy.data.objects[thumb_position_name].location = T_R.location

    for obj in bpy.data.collections[collection].objects:
        obj_name = obj.name
        if obj_name.endswith("_L"):
            continue
        try:
            if obj_name.startswith("I"):
                position_ball_name = f'i{finger_positions["i"]}'
            elif obj_name.startswith("M"):
                position_ball_name = f'm{finger_positions["m"]}'
            elif obj_name.startswith("R"):
                position_ball_name = f'a{finger_positions["a"]}'
            elif obj_name.startswith("P"):
                position_ball_name = f'ch{finger_positions["a"]}'
            else:
                print(f'Error happend. name: {obj_name}')
            bpy.data.objects[position_ball_name].location = obj.location

        except Exception as e:
            print(f"Error: {e}")


def add_random_rotation():
    """
    useage:这个方法用于在blender中给头发和裙子添加一些摆动效果
    """
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


def export_controller_info(file_name: str) -> None:
    """
    :param file_name: 输出文件名
    useage:这个方法用于在blender中将所有的控制器的位置和旋转信息输出到json文件
    """
    import json
    from collections import defaultdict
    import mathutils
    LeftHandPositions = bpy.data.collections['LeftHandPositions'].objects
    RotationCones = bpy.data.collections['RotationCones'].objects
    RightHandPositions = bpy.data.collections['RightHandPositions'].objects
    RightHandLines = bpy.data.collections['RightHandLines'].objects

    def nested_dict():
        return defaultdict(nested_dict)

    result = nested_dict()

    for obj in LeftHandPositions:
        obj_name = obj.name
        name_parts = obj_name.split('_', 2)
        type_name = name_parts[0]
        position_name = name_parts[1]
        if type_name == 'Fret':
            result['LEFT_FINGER_POSITIONS'][position_name] = obj.location
        elif type_name == 'Normal':
            controller_name = name_parts[2]
            result['NORMAL_LEFT_HAND_POSITIONS'][position_name][controller_name] = obj.location
        elif type_name == 'Outer':
            controller_name = name_parts[2]
            result['OUTER_LEFT_HAND_POSITIONS'][position_name][controller_name] = obj.location
        elif type_name == 'Inner':
            controller_name = name_parts[2]
            result['INNER_LEFT_HAND_POSITIONS'][position_name][controller_name] = obj.location
        else:
            print(f'Error happend. type: {type_name}, name: {obj_name}')

    for obj in RotationCones:
        obj_name = obj.name
        name_parts = obj_name.split('_', 2)
        type_name = name_parts[0]
        position_name = name_parts[1]
        controller_name = name_parts[2]
        result['ROTATIONS'][controller_name][type_name][position_name] = obj.rotation_euler

    for obj in RightHandPositions:
        obj_name = obj.name
        result['RIGHT_HAND_POSITIONS'][obj_name] = obj.location
    # 因为是读取的四元旋转值，所以代表手指运动方向的五根线都需要把旋转模式改成四元数，否则读取出来的值为变为[1,0,0,0]
    for obj in RightHandLines:
        obj_name = obj.name

        obj_quaternion_normalized = obj.rotation_quaternion.normalized()
        rot_matrix = obj_quaternion_normalized.to_matrix()

        vec = rot_matrix @ mathutils.Vector((0, 0, 1))
        print(f'{obj_name} quaternion: {vec}')
        result['RIGHT_HAND_LINES'][obj_name] = vec

    data = json.dumps(result, default=list, indent=4)

    with open(file_name, 'w') as f:
        f.write(data)
        print(f'Exported to {file_name}')


def connect_parent_to_child():
    """
    useage:这个方法用于在blender中将选中的骨骼的父骨骼的尾部连接到子骨骼的头部。之所以要这样做是因为blender在导入mmd模型时骨骼会出现奇怪的朝向，需要修正
    """

    # 切换到编辑模式
    bpy.ops.object.mode_set(mode='EDIT')
    selected_bones = bpy.context.selected_bones

    # 检测所有骨骼是parent的次数
    parent_count = {}
    for pose_bone in selected_bones:
        parent = pose_bone.parent
        if parent:
            if parent.name in parent_count:
                parent_count[parent.name] += 1
            else:
                parent_count[parent.name] = 1

    for pose_bone in selected_bones:
        parent = pose_bone.parent
        if parent and parent_count[parent.name] == 1:

            parent.tail = pose_bone.head


def add_damped_tracks():
    """
    useage:这个方法用于在blender中给选中的骨骼添加damped track约束
    """
    # 切换到姿态模式
    bpy.ops.object.mode_set(mode='POSE')

    # 获取所有选中的骨骼
    selected_bones = bpy.context.selected_pose_bones_from_active_object
    target_name = 'Asuka_arm'
    target = bpy.data.objects[target_name]

    for pose_bone in selected_bones:

        sub_target_bone_name = pose_bone.name.replace('hair', 'hair_dist')

        # 添加damped track约束
        pose_bone.constraints.new('DAMPED_TRACK')
        pose_bone.constraints['Damped Track'].target = target
        pose_bone.constraints['Damped Track'].subtarget = sub_target_bone_name


def remove_zero_influence_constraints():
    """
    useage:这个方法用于在blender中删除所有权重为0的约束
    """
    # 切换到姿态模式
    bpy.ops.object.mode_set(mode='POSE')

    # 获取所有选中的骨骼
    selected_bones = bpy.context.selected_pose_bones_from_active_object

    for pose_bone in selected_bones:
        for constraint in pose_bone.constraints:
            if constraint.influence == 0:
                pose_bone.constraints.remove(constraint)


def check_missing_texture(missing_file):
    """
    useage:这个方法用于在blender中检查所有材质是否有缺失的纹理
    """
    for mat in bpy.data.materials:
        try:
            for node in mat.node_tree.nodes:
                if node.type == 'TEX_IMAGE':
                    if node.image is not None:
                        print(node.image.name_full)
                        if node.image.name_full == missing_file:
                            print('Material', mat.name,
                                  f'uses the missing texture {missing_file}')
        except:
            print(mat.name, 'has no node tree')


def disable_toons_on_selected_object():
    """
    usage: This method disables the toon material effect on all materials of the selected object in Blender.
    """
    # 获取当前选择的对象
    obj = bpy.context.selected_objects[0]

    if obj and obj.type == 'MESH':  # 检查对象是否为网格类型
        # 遍历对象的所有材质
        for i in range(len(obj.material_slots)):
            # 确保材质槽有有效的材质
            material = obj.material_slots[i].material
            if material:
                # 检查材质是否包含MMD材料信息（适用于MMD相关场景）
                if hasattr(material, 'mmd_material'):
                    material.mmd_material.is_double_sided = False
                    material.mmd_material.enabled_toon_edge = False
                else:
                    print(
                        f"Material {material.name} does not have MMD material properties. Skipping.")
    else:
        print("No mesh object selected or no valid materials found.")


def convert_vrm_mat_to_blender():
    """
    usage: This method converts the VRM material to Blender material.
    """
    obj = bpy.context.selected_objects[0]
    if obj and obj.type == 'MESH':
        for i in range(len(obj.material_slots)):
            material = obj.material_slots[i].material
            if material:
                lit_color_node = None
                emission_node = None
                normal_node = None
                Princlipled_BSDF_node = None
                Normal_map_node = None

                for node in material.node_tree.nodes:
                    if node.type == 'BSDF_PRINCIPLED':
                        Princlipled_BSDF_node = node
                        continue
                    elif node.type == 'NORMAL_MAP':
                        Normal_map_node = node
                        continue
                    elif node.type == 'TEX_IMAGE' and node.image:
                        if node.label == 'Lit Color Texture':
                            lit_color_node = node
                            continue
                        elif node.label == 'Emissive Texture':
                            emission_node = node
                            continue
                        elif node.label == 'Normal Map Texture':
                            normal_node = node
                            continue
                    else:
                        material.node_tree.nodes.remove(node)

                if not Princlipled_BSDF_node:
                    Princlipled_BSDF_node = material.node_tree.nodes.new(
                        'ShaderNodeBsdfPrincipled')
                if not Normal_map_node:
                    Normal_map_node = material.node_tree.nodes.new(
                        'ShaderNodeNormalMap')

                if lit_color_node:
                    material.node_tree.links.new(
                        lit_color_node.outputs['Color'], Princlipled_BSDF_node.inputs['Base Color'])
                if emission_node:
                    material.node_tree.links.new(
                        emission_node.outputs['Color'], Princlipled_BSDF_node.inputs['Emission Color'])
                if normal_node:
                    material.node_tree.links.new(
                        normal_node.outputs['Color'], Normal_map_node.inputs['Color'])
                    material.node_tree.links.new(
                        Normal_map_node.outputs['Normal'], Princlipled_BSDF_node.inputs['Normal'])

                # 获取 Material Output 节点
                material_output_node = material.node_tree.nodes.get(
                    'Material Output')
                if not material_output_node:
                    material_output_node = material.node_tree.nodes.new(
                        'ShaderNodeOutputMaterial')
                # 连接 Princlipled_BSDF_node 到 Material Output 节点
                material.node_tree.links.new(
                    Princlipled_BSDF_node.outputs['BSDF'], material_output_node.inputs['Surface'])


def follow_lowest_foot(base_pivot_name: str, left_foot_name: str, right_foot_name: str, frames: int):
    """
    usage: 这个方法用于修正滑步的动作.使用方式是先用两个轴点left_foot_name和right_foot_name记录左右脚最低点的运动，然后用一个空轴点base_pivot_name来记录修正运动。最后面将骨骼的base_bone约束到这个修正后的空轴点上，就可以完成滑步的修正。
"""
    base_pivot = bpy.data.objects[base_pivot_name]

    left_foot = bpy.data.objects[left_foot_name]
    right_foot = bpy.data.objects[right_foot_name]
    pre_foot_position = [left_foot.location.copy(), right_foot.location.copy()]
    current_foot = None

    for i in range(1, frames+1):
        if i > 1:
            pre_foot_position = current_foot_position[:]
        # 先把时间轴调整到当前帧
        bpy.context.scene.frame_set(i)
        # 记录两只脚的当前位置
        current_foot_position = [
            left_foot.location.copy(), right_foot.location.copy()]
        # 这里取哪个值来判断高度，取决base_bone的朝向
        current_foot = left_foot if left_foot.location[2] <= right_foot.location[2] else right_foot
        current_foot_index = 0 if current_foot == left_foot else 1
        print(f'current_i:{i},current_foot_index: {current_foot_index}')

        offset = current_foot.location - \
            pre_foot_position[current_foot_index]
        base_pivot.location -= offset
        base_pivot.keyframe_insert(data_path="location")


def modify_daz_studio_bones():
    """
    usage: 将骨骼的自定义形状去掉
    """
    selected_bones = bpy.context.selected_pose_bones

    # 切换到编辑模式
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in selected_bones:
        if bone.name.startswith('l'):
            bone.name = bone.name[1:] + "_L"
        elif bone.name.startswith('r'):
            bone.name = bone.name[1:] + "_R"

    # 切换回pose模式
    bpy.ops.object.mode_set(mode='POSE')

    for bone in selected_bones:
        if bone.custom_shape:
            bone.custom_shape = None
        bone.use_ik_limit_x = False
        bone.use_ik_limit_y = False
        bone.use_ik_limit_z = False
        bone.lock_ik_x = False
        bone.lock_ik_y = False
        bone.lock_ik_z = False


def adjust_bone_rotation():
    """
    usage: 调整一定时间帧内的骨骼的旋转角度，主要用于将某些骨骼在每一帧都进行一样的旋转操作
    """
    # 设置当前帧
    current_frame = bpy.context.scene.frame_start

    # 获取选定的骨骼
    selected_bones = bpy.context.selected_pose_bones

    # 遍历每一帧
    while current_frame <= bpy.context.scene.frame_end:
        bpy.context.scene.frame_set(current_frame)

        bpy.ops.transform.rotate(value=0.483127, orient_axis='X', orient_type='GLOBAL', orient_matrix=((1, 0, 0), (0, 1, 0), (0, 0, 1)), orient_matrix_type='GLOBAL', constraint_axis=(
            True, False, False), mirror=False, snap=False, snap_elements={'INCREMENT'}, use_snap_project=False, snap_target='CLOSEST', use_snap_self=True, use_snap_edit=True, use_snap_nonedit=True, use_snap_selectable=False)

        bpy.ops.anim.keyframe_insert()

        # 移动到下一帧
        current_frame += 1


if __name__ == "__main__":
    pass
