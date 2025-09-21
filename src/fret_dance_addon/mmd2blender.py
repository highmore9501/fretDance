import bpy  # type: ignore
from mathutils import Matrix  # type: ignore


def process_wrist_bones(armature, base_bone_name: str, suffix: str = ""):
    """
    处理腕部骨骼，检查是否存在 腕 并根据需要创建 MCH_腕
    """

    # 获取骨架数据
    edit_bones = armature.data.edit_bones

    full_bone_name = base_bone_name + suffix

    # 检查是否存在full_bone_name
    wrist_bone = edit_bones.get(full_bone_name)
    if not wrist_bone:
        print(f"未找到 {full_bone_name} 骨骼")
        return

    # 检查是否存在mch_bone_name
    mch_bone_name = f"MCH_{full_bone_name}"
    mch_wrist_bone = edit_bones.get(mch_bone_name)

    if wrist_bone and not mch_wrist_bone:
        new_bone = edit_bones.new(mch_bone_name)
        new_bone.head = wrist_bone.head.copy()
        new_bone.tail = wrist_bone.tail.copy()
        new_bone.roll = wrist_bone.roll
        new_bone.parent = wrist_bone.parent

        # 关闭新骨骼的 deform 属性
        new_bone.use_deform = False

        # 将原来的骨骼设置为MCH骨骼的子级
        wrist_bone.parent = new_bone
        mch_wrist_bone = new_bone

        print(f"已创建 {mch_bone_name} 并设置父子关系")
    elif mch_wrist_bone:
        print(f"{mch_bone_name} 已存在，无需创建")

    # 检查腕捩的父级是不是mch_bone，如果不是就把父级设为mch_bone
    wrist_twist_bone = edit_bones.get(f"腕捩{suffix}")
    if wrist_twist_bone is None:
        print(f"未找到 {f'腕捩{suffix}'} 骨骼")
        side = "left" if suffix == ".L" else "right"
        wrist_twist_bone = edit_bones.get(f"arm {side} shoulder twist")
        if wrist_twist_bone is None:
            print(f"未找到 {f'arm {side} shoulder twist'} 骨骼")

    if wrist_twist_bone and wrist_twist_bone.parent != mch_wrist_bone:
        wrist_twist_bone.parent = mch_wrist_bone
        print(f"已设置{wrist_twist_bone.name}的父级为{wrist_twist_bone.parent.name}")
    else:
        print(f"{mch_bone_name} 已存在，无需创建")

    # 检查ひじ的父级是不是mch_bone，如果不是就把父级设为mch_bone
    fore_arm_bone = edit_bones.get(f"ひじ{suffix}")
    if fore_arm_bone and fore_arm_bone.parent != mch_wrist_bone:
        fore_arm_bone.parent = mch_wrist_bone
        print(f"已设置{fore_arm_bone.name}的父级为{fore_arm_bone.parent.name}")


def process_fore_arm_bones(armature, base_bone_name: str, suffix: str = ""):
    """
    处理腕部骨骼，检查是否存在 腕.L 并根据需要创建 MCH_腕.L
    """

    # 获取骨架数据
    edit_bones = armature.data.edit_bones

    full_bone_name = base_bone_name + suffix

    # 检查是否存在full_bone_name
    wrist_bone = edit_bones.get(full_bone_name)
    if not wrist_bone:
        print(f"未找到 {full_bone_name} 骨骼")
        return

    # 检查是否存在mch_bone_name
    mch_bone_name = f"MCH_{full_bone_name}"
    mch_wrist_bone = edit_bones.get(mch_bone_name)

    if wrist_bone and not mch_wrist_bone:
        new_bone = edit_bones.new(mch_bone_name)
        new_bone.head = wrist_bone.head.copy()
        new_bone.tail = wrist_bone.tail.copy()
        new_bone.roll = wrist_bone.roll
        new_bone.parent = wrist_bone.parent

        # 关闭新骨骼的 deform 属性
        new_bone.use_deform = False

        # 将原来的骨骼设置为MCH骨骼的子级
        wrist_bone.parent = new_bone

        mch_wrist_bone = new_bone

        print(f"已创建 {mch_bone_name} 并设置父子关系")
    elif mch_wrist_bone:
        print(f"{mch_bone_name} 已存在，无需创建")

    # 检查 wrist_bone 的父级是不是 mch_wrist_bone，如果不是就添加
    if mch_wrist_bone and mch_wrist_bone.parent.name != f"MCH_腕{suffix}":
        mch_wrist_bone.parent = edit_bones.get(f"MCH_腕{suffix}")
        print(f"已设置 {mch_wrist_bone.name} 的父级为 {mch_wrist_bone.parent.name}")

    # 检查腕捩的父级是不是mch_bone，如果不是就把父级设为mch_bone
    wrist_twist_bone = edit_bones.get(f"手捩{suffix}")
    if wrist_twist_bone is None:
        print(f"未找到 {f'手捩{suffix}'} 骨骼")
        side = "left" if suffix == ".L" else "right"
        wrist_twist_bone = edit_bones.get(f"arm {side} elbow twist")
        if wrist_twist_bone is None:
            print(f"未找到 {f'arm {side} elbow twist'} 骨骼")

    if wrist_twist_bone and wrist_twist_bone.parent != mch_wrist_bone:
        wrist_twist_bone.parent = mch_wrist_bone
        print(f"已设置{wrist_twist_bone.name}的父级为{wrist_twist_bone.parent.name}")

    # 检查手首的父级是不是mch_bone，如果不是就把父级设为mch_bone
    fore_arm_bone = edit_bones.get(f"手首{suffix}")
    if fore_arm_bone and fore_arm_bone.parent != mch_wrist_bone:
        fore_arm_bone.parent = mch_wrist_bone
        print(f"已设置{fore_arm_bone.name}的父级为{fore_arm_bone.parent.name}")


def create_finger_MCH_bones(armature):

    # 切换到编辑模式
    bpy.ops.object.mode_set(mode='EDIT')
    edit_bones = armature.data.edit_bones

    current_bones = []
    new_bones = []
    fingers = ["親指", "人指", "中指", "薬指", "小指"]
    # 有时候骨骼会用这种全角的索引数字，所以要处理一下
    full_indices = ["０", "１", "２", "３"]

    for finger in fingers:
        for index in range(0, 4):
            for suffix in [".L", ".R"]:
                full_bone_name = finger + str(index) + suffix
                # 检查是否存在full_bone_name
                finger_bone = edit_bones.get(full_bone_name)
                if not finger_bone:
                    print(f"未找到 {full_bone_name} 骨骼")
                    continue
                else:
                    current_bones.append(finger_bone)

    for finger in fingers:
        for index in full_indices:
            for suffix in [".L", ".R"]:
                full_bone_name = finger + str(index) + suffix
                # 检查是否存在full_bone_name
                finger_bone = edit_bones.get(full_bone_name)
                if not finger_bone:
                    print(f"未找到 {full_bone_name} 骨骼")
                    continue
                else:
                    current_bones.append(finger_bone)

                # 检查是否存在mch_bone_name

    for bone in current_bones:
        bone_copy_name = "MCH_" + bone.name
        bone_copy = edit_bones.get(bone_copy_name)
        if bone_copy:
            print(f"{bone_copy_name} 已存在，无需创建")
            continue
        # 复制骨骼
        bone_copy = bpy.context.object.data.edit_bones.new("MCH_" + bone.name)
        bone_copy.head = bone.head
        bone_copy.tail = bone.tail
        bone_copy.roll = bone.roll
        bone_copy.parent = bone.parent
        bone_copy.use_deform = False
        # 将现骨骼的connected选项去掉
        bone.use_connect = False
        # 将原骨骼的parent设置为新骨骼
        bone.parent = bone_copy
        new_bones.append(bone_copy)

    for copy_bone in new_bones:
        # 检测它的parent是否有MCH前缀的同名骨骼存在
        parent = copy_bone.parent
        if not parent:
            continue
        new_parent_name = "MCH_" + parent.name
        new_parent = bpy.context.object.data.edit_bones.get(new_parent_name)
        if new_parent:
            copy_bone.parent = new_parent
            # 设置与父级为connected
            copy_bone.use_connect = True


def make_target_bones(armature):
    # 获取骨架数据
    edit_bones = armature.data.edit_bones

    original_bones = ["手首", "肩"]
    suffixes = [".L", ".R"]

    for bone in original_bones:
        for suffix in suffixes:
            full_bone_name = bone + suffix
            # 检查是否存在full_bone_name
            original_bone = edit_bones.get(full_bone_name)
            if not original_bone:
                print(f"未找到 {full_bone_name} 骨骼，无法复制生成Tar骨骼")
                continue

            tar_bone_name = "Tar_" + full_bone_name
            # 检查是否存在tar_bone_name
            tar_bone = edit_bones.get(tar_bone_name)
            if not tar_bone:
                new_bone = edit_bones.new(tar_bone_name)
                new_bone.head = original_bone.head.copy()
                new_bone.tail = original_bone.tail.copy()
                new_bone.roll = original_bone.roll
                new_bone.parent = original_bone.parent

                # 创建新骨骼的子级
                new_bone.parent = original_bone

                # 将新骨骼在x轴上平稳0.5m
                offset = 0.5 if suffix == ".L" else -0.5
                new_bone.head.x += offset
                new_bone.tail.x += offset


def move_MCH_bones(armature, MCH_collection_name: str = "MCH"):
    """
    usage:这个方法用于在blender中将所有的MCH骨骼移动到MCH层
    """
    # 确保在姿态模式下操作
    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')

    # 获取当前活动的骨架对象
    if not armature or armature.type != 'ARMATURE':
        print("错误: 没有选中的骨架对象")
        return

    # 全选所有骨骼
    bpy.ops.pose.select_all(action='SELECT')

    # 获取或创建MCH骨骼集合
    mch_collection = None
    for collection in armature.data.collections:
        if collection.name == MCH_collection_name:
            mch_collection = collection
            break

    # 如果没有找到MCH集合，则创建一个
    if not mch_collection:
        mch_collection = armature.data.collections.new(MCH_collection_name)

    # 将所有包含'MCH'和"Tar"的骨骼分配到MCH集合中
    for pose_bone in bpy.context.selected_pose_bones:
        if 'MCH_' in pose_bone.name or 'Tar_' in pose_bone.name:
            # 将骨骼添加到MCH集合
            mch_collection.assign(pose_bone.bone)

            # 从其他集合中移除该骨骼
            for collection in armature.data.collections:
                if collection != mch_collection and pose_bone.bone.name in collection.bones:
                    collection.unassign(pose_bone.bone)


def move_obj_to_bone_position(armature, bone_name, obj_name):

    obj = bpy.data.objects.get(obj_name)
    if not obj:
        print(f"未找到对象 {obj_name}")
        return

    # 获取骨骼
    edit_bones = armature.data.edit_bones
    bone = edit_bones.get(bone_name)
    if not bone:
        print(f"未找到骨骼 {bone_name}")
        return

    # 获取骨骼的坐标
    bone_tail = bone.tail
    bone_matrix = bone_matrix = Matrix.Translation(bone_tail)
    # 应用骨骼的旋转矩阵
    bone_matrix = bone_matrix @ bone.matrix.to_3x3().to_4x4()

    obj.matrix_world = bone_matrix


def move_objs_to_bones(armature):
    set_parents()
    for suffix in ["L", "R"]:
        # 设置父子关系：让HP_*/TP_*对象成为Tar_肩/Tar_手首骨骼的子级
        obj_hp = bpy.data.objects.get("HP_" + suffix)
        obj_tp = bpy.data.objects.get("TP_" + suffix)
        bone_shoulder = armature.data.bones.get("Tar_肩." + suffix)
        bone_wrist = armature.data.bones.get("Tar_手首." + suffix)

        if obj_hp and bone_shoulder:
            # 设置HP_*为Tar_肩骨骼的子级
            obj_hp.parent = armature
            obj_hp.parent_type = 'BONE'
            obj_hp.parent_bone = "Tar_肩." + suffix
            obj_hp.location = (0, 0, 0)
            print("HP_" + suffix + "已设置成Tar_肩骨骼的子级")

        if obj_tp and bone_wrist:
            # 设置TP_*为Tar_手首骨骼的子级
            obj_tp.parent = armature
            obj_tp.parent_type = 'BONE'
            obj_tp.parent_bone = "Tar_手首." + suffix
            obj_tp.location = (0, 0, 0)
            print("TP_" + suffix + "已设置成Tar_手首骨骼的子级")

    for suffix in ["L", "R"]:
        move_obj_to_bone_position(armature, "ひじ."+suffix, "H_"+suffix)
        move_obj_to_bone_position(
            armature, "Tar_肩."+suffix, "HP_"+suffix)
        move_obj_to_bone_position(armature, "ひじ."+suffix, "H_rotation"+suffix)
        move_obj_to_bone_position(armature, "親指２."+suffix, "T_"+suffix)
        move_obj_to_bone_position(armature, "人指３."+suffix, "I_"+suffix)
        move_obj_to_bone_position(armature, "中指３."+suffix, "M_"+suffix)
        move_obj_to_bone_position(armature, "薬指３."+suffix, "R_"+suffix)
        move_obj_to_bone_position(armature, "小指３."+suffix, "P_"+suffix)


def add_ik_constraint_for_bone(armature, bone_name, target_name, pole_name=None, chain_length=3, enable=True):
    bone = armature.pose.bones.get(bone_name)
    target_obj = bpy.data.objects.get(target_name)
    pole_obj = bpy.data.objects.get(pole_name) if pole_name else None

    # 检查骨骼和目标对象是否存在
    if not bone or not target_obj:
        print(f"未找到骨骼 {bone_name} 或目标对象 {target_name}")
        return

    # 清除现有的IK约束
    for constraint in bone.constraints:
        if constraint.type == 'IK':
            bone.constraints.remove(constraint)

    # 添加IK约束
    ik_constraint = bone.constraints.new('IK')
    ik_constraint.target = target_obj
    ik_constraint.chain_count = chain_length

    # 设置极向目标（如果提供）
    if pole_obj is not None:
        ik_constraint.pole_target = pole_obj

    # 设置极向轴为 -Y 轴（通常用于手臂和腿部）
    ik_constraint.pole_angle = 0  # 可根据需要调整
    ik_constraint.enabled = enable

    print(f"已为骨骼 {bone_name} 添加IK约束")


def add_locked_track_constraint_for_bone(armature, bone_name, target_bone_name, enable=True):
    bone = armature.pose.bones.get(bone_name)
    target_bone = armature.pose.bones.get(target_bone_name)

    # 检查骨骼和目标对象是否存在
    if not bone or not target_bone:
        print(f"未找到骨骼 {bone_name} 或目标骨骼 {target_bone_name}")
        return

    # 清除现有的LOCKED_TRACK约束
    for constraint in bone.constraints:
        if constraint.type == 'LOCKED_TRACK':
            bone.constraints.remove(constraint)

    # 添加Locked Track约束
    locked_track_constraint = bone.constraints.new('LOCKED_TRACK')
    locked_track_constraint.target = armature  # 目标骨架对象
    locked_track_constraint.subtarget = target_bone_name  # 目标骨骼名称
    locked_track_constraint.track_axis = 'TRACK_Z'  # 跟踪轴向，可根据需要调整
    locked_track_constraint.lock_axis = 'LOCK_Y'    # 锁定轴向，可根据需要调整
    locked_track_constraint.enabled = enable

    print(f"已为骨骼 {bone_name} 添加Locked Track约束，目标为 {target_bone_name}")


def add_copy_rotation_constraint_for_bone(armature, bone_name, target_name, is_bone=False, copy_type='world', enable=True):
    """
    为骨骼添加复制旋转约束

    参数:
    armature: 骨骼对象
    bone_name: 要添加约束的骨骼名称
    target_name: 目标对象名称
    is_bone: 布尔值，True表示target_name是骨骼，False表示是常规物体
    copy_type: 复制类型，'world'表示world to world，'local'表示local to local
    """
    bone = armature.pose.bones.get(bone_name)

    # 检查骨骼是否存在
    if not bone:
        print(f"未找到骨骼 {bone_name}")
        return

    # 清除现有的COPY_ROTATION约束
    for constraint in bone.constraints:
        if constraint.type == 'COPY_ROTATION':
            bone.constraints.remove(constraint)

    # 添加Copy Rotation约束
    copy_rotation_constraint = bone.constraints.new('COPY_ROTATION')

    if is_bone:
        # 目标是骨骼
        copy_rotation_constraint.target = armature
        copy_rotation_constraint.subtarget = target_name
    else:
        # 目标是常规物体
        target_obj = bpy.data.objects.get(target_name)
        if not target_obj:
            print(f"未找到目标对象 {target_name}")
            return
        copy_rotation_constraint.target = target_obj

    # 设置复制类型
    if copy_type == 'local':
        copy_rotation_constraint.target_space = 'LOCAL'
        copy_rotation_constraint.owner_space = 'LOCAL'
        # 只复制Y轴旋转值
        copy_rotation_constraint.use_x = False
        copy_rotation_constraint.use_y = True
        copy_rotation_constraint.use_z = False
    else:  # 默认为world
        copy_rotation_constraint.target_space = 'WORLD'
        copy_rotation_constraint.owner_space = 'WORLD'

    copy_rotation_constraint.enabled = enable

    print(f"已为骨骼 {bone_name} 添加Copy Rotation约束，目标为 {target_name}")


def set_iks(armature):
    # 确保在姿态模式下操作
    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')

    # 获取当前活动的骨架对象
    if not armature or armature.type != 'ARMATURE':
        print("错误: 没有选中的骨架对象")
        return

    # 在MCH_ひじ.L上设置ik，目标是H_L,pole是HP_L,层数是3
    for suffix in ["L", "R"]:
        add_ik_constraint_for_bone(
            armature, f"MCH_ひじ.{suffix}", f"H_{suffix}", f"HP_{suffix}", 2)
        add_ik_constraint_for_bone(
            armature, "MCH_親指２."+suffix, "T_"+suffix, "TP_"+suffix)
        add_ik_constraint_for_bone(armature, "MCH_人指３."+suffix, "I_"+suffix)
        add_ik_constraint_for_bone(armature, "MCH_中指３."+suffix, "M_"+suffix)
        add_ik_constraint_for_bone(armature, "MCH_薬指３."+suffix, "R_"+suffix)
        add_ik_constraint_for_bone(armature, "MCH_小指３."+suffix, "P_"+suffix)


def set_locked_tracks(armature):
    # 确保在姿态模式下操作
    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')

    # 获取当前活动的骨架对象
    if not armature or armature.type != 'ARMATURE':
        print("错误: 没有选中的骨架对象")
        return

    fingers = ["親指", "人指", "中指", "薬指", "小指"]
    # 有时候骨骼会用这种全角的索引数字，所以要处理一下
    full_indices = ["０", "１", "２", "３"]

    for finger in fingers:
        for index in range(0, 4):
            for suffix in [".L", ".R"]:
                full_bone_name = finger + str(index) + suffix
                target_bone_name = "Tar_手首" + suffix
                add_locked_track_constraint_for_bone(
                    armature, full_bone_name, target_bone_name, False)

    for finger in fingers:
        for index in full_indices:
            for suffix in [".L", ".R"]:
                full_bone_name = finger + str(index) + suffix
                target_bone_name = "Tar_手首" + suffix
                add_locked_track_constraint_for_bone(
                    armature, full_bone_name, target_bone_name, False)

    for bone_name in ["腕捩", "腕"]:
        for suffix in [".L", ".R"]:
            add_locked_track_constraint_for_bone(
                armature, bone_name + suffix, "Tar_肩" + suffix)


def set_copy_rotations(armature):
    # 确保在姿态模式下操作
    if bpy.context.mode != 'POSE':
        bpy.ops.object.mode_set(mode='POSE')

    # 获取当前活动的骨架对象
    if not armature or armature.type != 'ARMATURE':
        print("错误: 没有选中的骨架对象")
        return

    for suffix in ["L", "R"]:
        add_copy_rotation_constraint_for_bone(
            armature, "手首."+suffix, "H_rotation_"+suffix, False, 'world')
        add_copy_rotation_constraint_for_bone(
            armature, "手捩."+suffix, "手首."+suffix, True, 'local')
        side = "left" if suffix == "L" else "right"
        fore_arm_name = f'arm {side} elbow twist'
        add_copy_rotation_constraint_for_bone(
            armature, fore_arm_name, "手首."+suffix, True, 'local')


def set_parents():
    for suffix in ["L", "R"]:
        rotation_controller_name = f'H_rotation_{suffix}'
        hand_controller_name = f'H_{suffix}'
        rotation_controller = bpy.data.objects[rotation_controller_name]
        hand_controller = bpy.data.objects[hand_controller_name]
        if rotation_controller and hand_controller:
            rotation_controller.parent = hand_controller
            rotation_controller.location = (0, 0, 0)
            print(f"已设置 {rotation_controller_name} 的父对象为 {hand_controller_name}")
        else:
            print(f"未找到对象 {rotation_controller_name} 或 {hand_controller_name}")


def mmd2blender():
    # 获取当前活动的骨架对象
    armature = bpy.context.active_object
    if not armature or armature.type != 'ARMATURE':
        print("请选择一个骨架对象")
        return

    # 确保在编辑模式下操作
    if bpy.context.mode != 'EDIT_ARMATURE':
        bpy.ops.object.mode_set(mode='EDIT')

    process_wrist_bones(armature, "腕", ".L")
    process_wrist_bones(armature, "腕", ".R")

    process_fore_arm_bones(armature, "ひじ", ".L")
    process_fore_arm_bones(armature, "ひじ", ".R")

    create_finger_MCH_bones(armature)
    make_target_bones(armature)
    move_objs_to_bones(armature)
    move_MCH_bones(armature)

    set_iks(armature)
    set_locked_tracks(armature)
    set_copy_rotations(armature)


if __name__ == "__main__":
    mmd2blender()
