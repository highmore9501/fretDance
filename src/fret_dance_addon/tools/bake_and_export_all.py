import bpy  # type: ignore
import os
from typing import Set, Dict, List


def export_objects_to_fbx(export_path: str = "//exports/"):
    """
    导出Blender场景中的物体到多个FBX文件，根据物体类型采用不同策略

    Args:
        export_path: 导出路径，默认为当前blend文件目录下的exports文件夹
    """

    # 确保导出路径存在
    if export_path.startswith("//"):
        # 相对于blend文件的路径
        base_path = os.path.dirname(bpy.data.filepath)
        full_export_path = os.path.join(base_path, export_path[2:])
    else:
        full_export_path = export_path

    if not os.path.exists(full_export_path):
        os.makedirs(full_export_path)

    # 记录已处理的对象以避免重复导出
    processed_objects: Set[str] = set()
    armature_mesh_pairs: Dict[str, List[str]] = {}

    # 收集有shape key动画的网格体
    shape_key_animated_meshes: List[bpy.types.Object] = []

    # 遍历所有可见物体
    for obj in bpy.context.scene.objects:
        if not obj.visible_get() or obj.name in processed_objects:
            continue

        if obj.type == 'ARMATURE':
            # 处理骨骼及其关联的蒙皮网格
            process_armature(obj, full_export_path,
                             processed_objects, armature_mesh_pairs)

        elif obj.type == 'MESH':
            # 处理网格物体
            if has_shape_key_animation(obj):
                # 有shape key动画的网格体收集起来
                shape_key_animated_meshes.append(obj)
                processed_objects.add(obj.name)
            elif has_animation(obj):
                # 有其他动画的网格物体
                process_animated_mesh(obj, full_export_path, processed_objects)
            else:
                # 静态网格物体
                process_static_mesh(obj, full_export_path, processed_objects)

    # 统一处理有shape key动画的网格体
    if shape_key_animated_meshes:
        process_shape_key_animated_meshes(
            shape_key_animated_meshes, full_export_path)

    print(
        f"导出完成，共导出 {len(processed_objects) + len(shape_key_animated_meshes)} 个物体")


def process_armature(armature_obj: bpy.types.Object, export_path: str,
                     processed_objects: Set[str], armature_mesh_pairs: Dict[str, List[str]]):
    """
    处理骨骼及其关联的蒙皮网格

    Args:
        armature_obj: 骨骼对象
        export_path: 导出路径
        processed_objects: 已处理对象集合
        armature_mesh_pairs: 骨骼-网格配对字典
    """
    # 查找与该骨骼关联的网格
    associated_meshes = []
    for obj in bpy.data.objects:
        if obj.type == 'MESH' and obj.find_armature() == armature_obj:
            associated_meshes.append(obj)

    if not associated_meshes:
        # 没有关联网格的骨骼，直接导出骨骼
        export_armature_only(armature_obj, export_path)
        processed_objects.add(armature_obj.name)
        return

    # 记录骨骼-网格配对
    armature_mesh_pairs[armature_obj.name] = [
        mesh.name for mesh in associated_meshes]

    # 烘焙骨骼动画
    bake_armature_animation(armature_obj, associated_meshes)

    # 导出骨骼和关联的网格
    filename = f"{armature_obj.name}.fbx"
    filepath = os.path.join(export_path, filename)

    # 选择骨骼和关联的网格
    bpy.ops.object.select_all(action='DESELECT')
    armature_obj.select_set(True)
    for mesh in associated_meshes:
        mesh.select_set(True)

    # 设置活动对象
    bpy.context.view_layer.objects.active = armature_obj

    # 导出FBX
    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=True,
        bake_space_transform=True,
        object_types={'ARMATURE', 'MESH'},
        use_mesh_modifiers=True,
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        axis_forward='-Z',
        axis_up='Y'
    )

    # 标记为已处理
    processed_objects.add(armature_obj.name)
    for mesh in associated_meshes:
        processed_objects.add(mesh.name)

    print(
        f"导出骨骼 {armature_obj.name} 及其网格: {[m.name for m in associated_meshes]}")


def export_armature_only(armature_obj: bpy.types.Object, export_path: str):
    """
    导出单独的骨骼对象

    Args:
        armature_obj: 骨骼对象
        export_path: 导出路径
    """
    filename = f"{armature_obj.name}_skeleton.fbx"
    filepath = os.path.join(export_path, filename)

    bpy.ops.object.select_all(action='DESELECT')
    armature_obj.select_set(True)
    bpy.context.view_layer.objects.active = armature_obj

    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=True,
        bake_space_transform=True,
        object_types={'ARMATURE'},
        add_leaf_bones=False,
        primary_bone_axis='Y',
        secondary_bone_axis='X',
        axis_forward='-Z',
        axis_up='Y'
    )

    print(f"导出骨骼 {armature_obj.name}")


def bake_armature_animation(armature_obj: bpy.types.Object, meshes: List[bpy.types.Object]):
    """
    烘焙骨骼动画到网格

    Args:
        armature_obj: 骨骼对象
        meshes: 关联的网格对象列表
    """
    # 这里可以添加骨骼动画烘焙逻辑
    # 在实际使用中，可能需要根据具体需求实现动画烘焙
    pass


def has_animation(obj: bpy.types.Object) -> bool:
    """
    检查对象是否有动画

    Args:
        obj: 要检查的对象

    Returns:
        bool: 是否有动画
    """
    # 检查是否有动画数据
    if obj.animation_data:
        return True

    # 检查是否有驱动器
    if obj.data and hasattr(obj.data, 'shape_keys') and obj.data.shape_keys:
        if obj.data.shape_keys.animation_data:
            return True

    # 检查约束
    for constraint in obj.constraints:
        if constraint.animation_data:
            return True

    return False


def has_shape_key_animation(obj: bpy.types.Object) -> bool:
    """
    检查对象是否有shape key动画

    Args:
        obj: 要检查的对象

    Returns:
        bool: 是否有shape key动画
    """
    # 检查是否有shape key以及shape key动画数据
    if obj.data and hasattr(obj.data, 'shape_keys') and obj.data.shape_keys:
        if obj.data.shape_keys.animation_data:
            return True
    return False


def process_shape_key_animated_meshes(objects: List[bpy.types.Object], export_path: str):
    """
    统一处理有shape key动画的网格体

    Args:
        objects: 有shape key动画的网格体列表
        export_path: 导出路径
    """
    if not objects:
        return

    filename = "shape_key_animated_meshes.fbx"
    filepath = os.path.join(export_path, filename)

    # 选择所有有shape key动画的网格体
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:
        obj.select_set(True)

    # 设置第一个对象为活动对象
    bpy.context.view_layer.objects.active = objects[0]

    # 导出FBX
    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=True,
        bake_space_transform=True,
        object_types={'MESH'},
        use_mesh_modifiers=True,
        axis_forward='-Z',
        axis_up='Y'
    )

    print(
        f"导出 {len(objects)} 个有shape key动画的网格体: {[obj.name for obj in objects]}")


def process_animated_mesh(obj: bpy.types.Object, export_path: str, processed_objects: Set[str]):
    """
    处理有动画的网格物体（非shape key动画）

    Args:
        obj: 网格对象
        export_path: 导出路径
        processed_objects: 已处理对象集合
    """
    # 烘焙动画到网格（如果需要）
    bake_mesh_animation(obj)

    # 导出网格
    filename = f"{obj.name}_animated.fbx"
    filepath = os.path.join(export_path, filename)

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=True,
        bake_space_transform=True,
        object_types={'MESH'},
        use_mesh_modifiers=True,
        axis_forward='-Z',
        axis_up='Y'
    )

    processed_objects.add(obj.name)
    print(f"导出动画网格 {obj.name}")


def bake_mesh_animation(obj: bpy.types.Object):
    """
    烘焙网格动画

    Args:
        obj: 网格对象
    """
    # 这里可以添加动画烘焙逻辑
    # 例如约束动画烘焙等
    pass


def process_static_mesh(obj: bpy.types.Object, export_path: str, processed_objects: Set[str]):
    """
    处理静态网格物体

    Args:
        obj: 网格对象
        export_path: 导出路径
        processed_objects: 已处理对象集合
    """
    filename = f"{obj.name}.fbx"
    filepath = os.path.join(export_path, filename)

    bpy.ops.object.select_all(action='DESELECT')
    obj.select_set(True)
    bpy.context.view_layer.objects.active = obj

    bpy.ops.export_scene.fbx(
        filepath=filepath,
        use_selection=True,
        bake_space_transform=True,
        object_types={'MESH'},
        use_mesh_modifiers=True,
        axis_forward='-Z',
        axis_up='Y'
    )

    processed_objects.add(obj.name)
    print(f"导出静态网格 {obj.name}")


# 使用示例
if __name__ == "__main__":
    # 可以通过修改export_path参数来指定导出路径
    export_objects_to_fbx("//exports/")
