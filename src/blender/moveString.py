import bpy
import bmesh
import mathutils


def move_string(offset: float):
    # 确保处于编辑模式
    if bpy.context.object.mode != 'EDIT':
        bpy.ops.object.mode_set(mode='EDIT')

    # 获取 bmesh 对象
    bm = bmesh.from_edit_mesh(bpy.context.object.data)

    # 获取原始向量
    original_vector = mathutils.Vector((0, 0, 1))
    # 获取旋转矩阵
    rotation_matrix = bpy.data.objects['string_move_direction'].rotation_euler.to_matrix(
    )
    # 将旋转矩阵应用到原始向量上
    rotated_vector = rotation_matrix @ original_vector

    # 计算当前选中所有顶点的中心点位置
    selected_points = [v for v in bm.verts if v.select]
    if not selected_points:
        return
    center = mathutils.Vector()
    for v in selected_points:
        center += v.co
    center /= len(selected_points)

    # 对所有选中的点再次遍历，寻找离中心点最远的距离
    max_distance = 0
    for v in selected_points:
        distance = (v.co - center).length
        if distance > max_distance:
            max_distance = distance

    # 将所有选中的点沿着direction方向移动max_distance
    for v in selected_points:
        distance = (v.co - center).length
        ratio = (max_distance - distance) / max_distance
        v.co += offset * rotated_vector * ratio**2  # 使用二次函数来计算移动距离

    # 更新 bmesh 到 mesh
    bmesh.update_edit_mesh(bpy.context.object.data)
