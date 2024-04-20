# 一些在blender里跑的工具脚本
import bpy
import mathutils


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

    ik_pivot_bones = ["Pinky_IK_pivot_L", "IndexFinger_IK_pivot_L",
                      "Ring_IK_pivot_L", "MiddleFinger_IK_pivot_L", "Thumb_IK_pivot_L"]

    armature = "Kamisato IK_arm"

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
                        result[obj_name] = {
                            "position": [obj_info.x, obj_info.y, obj_info.z],
                        }
                    else:
                        # 旋转控制器
                        obj_info = obj.rotation_euler
                        result[obj_name] = {
                            "rotation": [obj_info.x, obj_info.y, obj_info.z],
                        }
                except:
                    pass

    # 选中armature
    bpy.context.view_layer.objects.active = bpy.data.objects[armature]
    # 切换到pose mode
    bpy.ops.object.mode_set(mode='POSE')
    # 遍历所有骨骼
    for bone in bpy.context.object.pose.bones:
        bone_name = bone.name
        if bone_name in ik_pivot_bones:
            bone_info = bone.location
            result[bone_name] = {
                "position": [bone_info.x, bone_info.y, bone_info.z],
            }
    # 切换到object mode
    bpy.ops.object.mode_set(mode='OBJECT')

    print(result)


def import_controller_info(data):
    collections = ['PositionControllers',
                   'RotationControllers', 'PivotControllers', 'RightFingerVector']

    ik_pivot_bones = ["Pinky_IK_pivot_L", "IndexFinger_IK_pivot_L",
                      "Ring_IK_pivot_L", "MiddleFinger_IK_pivot_L", "Thumb_IK_pivot_L"]

    armature = "Kamisato IK_arm"

    for collection in collections:
        for obj in bpy.data.collections[collection].objects:
            obj_name = obj.name
            try:
                if collection != "RotationControllers" and collection != "RightFingerVector":
                    # 位置控制器
                    obj.location = data[obj_name]["position"]
                else:
                    # 旋转控制器
                    obj.rotation_euler = data[obj_name]["rotation"]
            except:
                pass

    # 选中armature
    bpy.context.view_layer.objects.active = bpy.data.objects[armature]
    # 切换到pose mode
    bpy.ops.object.mode_set(mode='POSE')
    # 遍历所有骨骼
    for bone in bpy.context.object.pose.bones:
        bone_name = bone.name
        if bone_name in ik_pivot_bones:
            try:
                bone_info = data[bone_name]
                bone.location = bone_info["position"]
            except:
                pass

    # 切换到object mode
    bpy.ops.object.mode_set(mode='OBJECT')


def export_positions(collection):
    result = {}
    for obj in bpy.data.collections[collection].objects:
        obj_name = obj.name
        obj_info = obj.matrix_world.to_translation()
        result[obj_name] = {
            "position": [obj_info.x, obj_info.y, obj_info.z],
        }
    print(result)


def export_directions(collection):
    result = {}
    for obj in bpy.data.collections[collection].objects:
        obj_name = obj.name
        rotation_vector = mathutils.Vector((0, 0, 1))  # Z-axis vector
        rotation_vector.rotate(obj.rotation_euler)
        unit_vector = rotation_vector.normalized()
        if not obj_name.startswith('T'):
            unit_vector = -unit_vector
        result[obj_name] = {
            "direction": [unit_vector.x, unit_vector.y, unit_vector.z],
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


if __name__ == "__main__":
    pass
