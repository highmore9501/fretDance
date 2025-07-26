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


def calculate_fret_positions(num_fret):
    """
    计算每个品格的位置。
    num_fret: 品格的数量
    """
    # 弦的长度为1（我们将其归一化）
    string_length = 1.0
    # 使用12平均律来计算每个品格的位置
    fret_position = string_length - (string_length / (2 ** (num_fret / 12.0)))
    return fret_position


def find_closest_division(fret_position, num_divisions):
    """
    找出品格离哪个分割线最近。
    fret_position: 品格的位置
    num_divisions: 分割线的数量
    """
    division_size = 1.0 / num_divisions
    closest_division = round(fret_position / division_size)
    return closest_division


def rename_shape_key():
    """
    useage:rename current object's shape key name,current object must be a string and its name ends with a number
    """
    current_object = bpy.context.active_object
    current_string_index = current_object.name[-1]
    for shape_key in current_object.data.shape_keys.key_blocks:
        shape_key_name = shape_key.name
        if not shape_key_name.startswith("s"):
            shape_key.name = f"s{current_string_index}" + shape_key_name


def make_string_shape_keys(num_divisions: int = 80, offset_ratio: float = 0.0025):
    current_object = bpy.context.object

    # 计算弦的实际长度（Z轴方向）
    z_coords = [v.co.z for v in current_object.data.vertices]
    string_length = max(z_coords) - min(z_coords)

    # 基于弦长计算实际offset值
    actual_offset = string_length * offset_ratio

    # 检查是否有basis shape key，没有就生成一个
    if not current_object.data.shape_keys:
        current_object.shape_key_add(name='Basis')

    # 如果有其它shape key，那么就删除
    for shape_key in current_object.data.shape_keys.key_blocks:
        if shape_key.name != 'Basis':
            current_object.shape_key_remove(shape_key)

    # 切换到编辑模式并获取bmesh对象
    bpy.ops.object.mode_set(mode='EDIT')
    bm = bmesh.from_edit_mesh(current_object.data)

    # 将所有顶点按z轴值由高到低进行排序
    all_vertices = sorted(bm.verts, key=lambda v: v.co.z, reverse=True)
    all_bm_vertices_ids = [v.index for v in all_vertices]

    all_loops = num_divisions + 1
    num_vertices_per_loop = len(bm.verts) // all_loops

    real_divisions = num_divisions + 1

    frets_info = []
    for num_fret in range(0, 21):
        fret_position = calculate_fret_positions(num_fret)
        closest_division = find_closest_division(
            fret_position, real_divisions)
        frets_info.append({
            'num_fret': num_fret,
            'closest_division': closest_division
        })

    for fret in range(0, 21):
        # 切换回object模式
        if bpy.context.object.mode != 'OBJECT':
            bpy.ops.object.editmode_toggle()
        # 添加新的shape key，名字为fret{fret}
        new_shape_key = current_object.shape_key_add(
            name=f'fret{fret}', from_mix=False)
        # 将shape key的值设置为1
        new_shape_key.value = 1

        # 将新添加的shape key设为当前激活的shape key
        bpy.context.object.active_shape_key_index = len(
            current_object.data.shape_keys.key_blocks) - 1

        # 切换到编辑模式并获取bmesh对象
        bpy.ops.object.mode_set(mode='EDIT')
        bm = bmesh.from_edit_mesh(current_object.data)

        closest_division = frets_info[fret]['closest_division']
        deselected_vertices_num = closest_division * num_vertices_per_loop
        current_selected_vertices_ids = all_bm_vertices_ids[deselected_vertices_num:]

        # 更新bmesh的索引表
        bm.verts.ensure_lookup_table()

        # 选中current_selected_vertices中的每一个顶点
        bpy.ops.mesh.select_all(action='DESELECT')
        for id in current_selected_vertices_ids:
            bm.verts[id].select = True

        move_string(actual_offset)
        # 切换回object模式
        bpy.ops.object.editmode_toggle()
        # 更新场景
        bpy.context.view_layer.update()
        new_shape_key.value = 0

    # 全部好了以后重命名shape key
    rename_shape_key()


make_string_shape_keys()
