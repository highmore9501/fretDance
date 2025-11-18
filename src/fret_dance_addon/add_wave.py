import bpy  # type: ignore


def add_wave_constraints():
    """
    添加波浪约束，主要为头发或者裙子添加一些波浪效果
    """

    # 获取当前选中的骨骼
    obj = bpy.context.active_object
    if obj is None or obj.type != 'ARMATURE':
        print("请选中一个骨架对象")
        return

    armature = obj
    bones = armature.data.bones
    pose_bones = armature.pose.bones

    # 确保在pose mode
    if bpy.context.mode != 'POSE':
        print("请在pose mode下运行此脚本")
        return

    # 获取所有选中的骨骼
    selected_bones = bpy.context.selected_pose_bones
    if not selected_bones:
        print("请至少选中一个骨骼")
        return

    # 解析顶点组名称中的数字
    def get_point_number(point_name):
        if point_name.startswith("point"):
            try:
                return int(point_name[5:])
            except ValueError:
                return 1
        return 1

     # 为每个选中的骨骼执行逻辑
    for selected_bone in selected_bones:
        # 查找当前骨骼的damped track约束器
        damped_track_constraint = None
        for constraint in selected_bone.constraints:
            if constraint.type == 'DAMPED_TRACK':
                damped_track_constraint = constraint
                break

        if damped_track_constraint is None:
            print("选中的骨骼没有damped track约束器")
            return

        # 记录约束器的目标、顶点组和强度
        target = damped_track_constraint.target
        vertex_group = damped_track_constraint.subtarget
        strength = damped_track_constraint.influence

        point_num = get_point_number(vertex_group)
        original_strength = strength

        # 新增变量来跟踪变化方向
        strength_direction = 1  # 1表示增加，-1表示减少
        point_direction = 1     # 1表示增加，-1表示减少

        # 遍历子骨骼
        current_bone = selected_bone
        while True:
            # 查找当前骨骼的第一个子骨骼
            child_bone = None
            for bone in pose_bones:
                if bone.parent == current_bone:
                    child_bone = bone
                    break

            # 如果没有子骨骼，则退出循环
            if child_bone is None:
                break

            # 检查子骨骼是否已经有damped track约束器
            has_damped_track = False
            for constraint in child_bone.constraints:
                if constraint.type == 'DAMPED_TRACK':
                    has_damped_track = True
                    break

            # 如果没有damped track约束器，则添加一个
            if not has_damped_track:
                new_constraint = child_bone.constraints.new('DAMPED_TRACK')
                new_constraint.target = target

                # 更新顶点组名称（按递增或递减规律）
                if point_direction == 1:
                    point_num += 1
                    if point_num >= 5:  # 到达最大值point5后开始递减
                        point_direction = -1
                else:
                    point_num -= 1
                    if point_num <= 1:  # 到达最小值point1后保持
                        point_direction = 1 if point_num > 1 else point_direction

                new_constraint.subtarget = f"point{point_num}"

                # 更新强度（按递增或递减规律）
                if strength_direction == 1:
                    strength += 0.1
                    if strength >= 1.0:  # 到达最大值1.0后开始递减
                        strength_direction = -1
                else:
                    strength -= 0.1
                    if strength <= 0.1:  # 到达最小值0.1后保持
                        strength_direction = 1 if strength < 1.0 else strength_direction

                new_constraint.influence = round(strength, 1)  # 四舍五入避免浮点误差

            # 移动到下一个子骨骼
            current_bone = child_bone


# 运行函数
add_wave_constraints()
