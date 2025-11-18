import bpy  # type: ignore


def move_deform_bones_from_mesh_to_def_collection():
    """
    根据选中的skinned mesh，查找其顶点组对应的骨骼，
    并将其中带有deform属性的骨骼移动到DEF骨骼集合中
    """
    # 检查是否有选中的对象
    obj = bpy.context.active_object
    if not obj or obj.type != 'MESH':
        print("请选中一个网格对象")
        return

    # 获取网格对象的顶点组
    vertex_groups = obj.vertex_groups
    if not vertex_groups:
        print("选中的网格对象没有顶点组")
        return

    # 查找与网格关联的骨骼对象
    armature = None
    for modifier in obj.modifiers:
        if modifier.type == 'ARMATURE' and modifier.object:
            armature = modifier.object
            break

    if not armature or armature.type != 'ARMATURE':
        print("未找到与网格关联的骨骼对象")
        return

    print(f"找到关联的骨骼对象: {armature.name}")

    # 收集顶点组名称
    vertex_group_names = [vg.name for vg in vertex_groups]
    print(f"找到 {len(vertex_group_names)} 个顶点组: {vertex_group_names}")

    # 切换到骨骼对象的Pose Mode
    original_object = bpy.context.active_object
    original_mode = bpy.context.mode

    # 设置激活对象为骨骼
    bpy.context.view_layer.objects.active = armature
    bpy.ops.object.mode_set(mode='POSE')

    try:
        # 获取骨骼数据
        armature_data = armature.data

        # 创建或获取DEF骨骼集合
        collection_name = "DEF"
        if collection_name not in armature_data.collections:
            def_collection = armature_data.collections.new(collection_name)
            print(f"创建骨骼集合: {collection_name}")
        else:
            def_collection = armature_data.collections[collection_name]
            print(f"使用现有骨骼集合: {collection_name}")

        # 记录处理的骨骼数量
        processed_count = 0
        moved_count = 0

        # 遍历所有顶点组名称，查找对应的骨骼
        for vg_name in vertex_group_names:
            bone = armature_data.bones.get(vg_name)
            if bone:
                processed_count += 1
                # 检查骨骼是否具有deform属性
                if bone.use_deform:
                    # 将骨骼添加到DEF集合
                    # 注意：在Pose Mode下，我们需要通过bone来访问对应的pose bone
                    pose_bone = armature.pose.bones.get(vg_name)
                    if pose_bone:
                        # 需要切换到Edit Mode来操作骨骼集合
                        bpy.ops.object.mode_set(mode='EDIT')
                        edit_bone = armature.data.edit_bones.get(vg_name)
                        if edit_bone:
                            def_collection.assign(edit_bone)
                            moved_count += 1
                            print(
                                f"将骨骼 '{vg_name}' 添加到 '{collection_name}' 集合")
                        bpy.ops.object.mode_set(mode='POSE')
                else:
                    print(f"骨骼 '{vg_name}' 不具有deform属性，跳过")
            else:
                print(f"未找到与顶点组 '{vg_name}' 对应的骨骼")

        print(
            f"处理完成: 检查了 {processed_count} 个骨骼，将 {moved_count} 个deform骨骼移动到'{collection_name}'集合")

    finally:
        # 恢复原始状态
        bpy.context.view_layer.objects.active = original_object
        if original_mode == 'EDIT_MESH':
            bpy.ops.object.mode_set(mode='EDIT')
        elif original_mode == 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')
        else:
            bpy.ops.object.mode_set(mode='OBJECT')

# 执行函数


move_deform_bones_from_mesh_to_def_collection()
