# 一些在blender里跑的工具脚本
import bpy


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


def export_controller_info():
    collections = ['PositionControllers',
                   'RotationControllers', 'PivotControllers']

    ik_pivot_bones = ["Pinky_IK_pivot_L", "IndexFinger_IK_pivot_L",
                      "Ring_IK_pivot_L", "MiddleFinger_IK_pivot_L", "Thumb_IK_pivot_L"]

    armature = "Kamisato IK_arm"

    result = {}

    for collection in collections:
        # 遍历所有collection里的的物体
        for obj in bpy.data.collections[collection].objects:
            obj_name = obj.name
            if collection != "RotationControllers":
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
    all_controllers = [
        "R_L", "RP_L", "R_rotation_L",
        "M_L", "MP_L", "M_rotation_L",
        "I_L", "IP_L", "I_rotation_L",
        "P_L", "PP_L", "P_rotation_L",
        "H_L", "HP_L", "H_rotation_X_L", "H_rotation_Y_L",
        "T_L", "TP_L", "T_rotation_L"
    ]

    all_ik_pivot_bones = ["Pinky_IK_pivot_L", "IndexFinger_IK_pivot_L",
                          "Ring_IK_pivot_L", "MiddleFinger_IK_pivot_L", "Thumb_IK_pivot_L"]
    armature = "Kamisato IK_arm"

    for controller in all_controllers:
        obj = bpy.data.objects[controller]
        value = data[controller]
        if "rotation" in controller:
            obj.rotation_euler = value["rotation"]
        else:
            obj.location = value["position"]

    # 选中armature
    bpy.context.view_layer.objects.active = bpy.data.objects[armature]
    # 切换到pose mode
    bpy.ops.object.mode_set(mode='POSE')
    # 遍历所有骨骼
    for bone in bpy.context.object.pose.bones:
        bone_name = bone.name
        if bone_name in all_ik_pivot_bones:
            try:
                bone_info = data[bone_name]
                bone.location = bone_info["position"]
            except:
                pass

    # 切换到object mode
    bpy.ops.object.mode_set(mode='OBJECT')


if __name__ == "__main__":
    pass
