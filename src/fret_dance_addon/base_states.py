
from enum import IntEnum, Enum
import json
import os
from collections import defaultdict
import mathutils
import bpy  # type: ignore


class Instruments(IntEnum):
    FINGER_STYLE_GUITAR = 0
    ELECTRIC_GUITAR = 1
    BASS = 2


class BasePositions(Enum):
    P0 = 'P0'
    P1 = 'P1'
    P2 = 'P2'
    P3 = 'P3'
    P4 = 'P4'


class LeftHandStates(Enum):
    NORMAL = "Normal"
    OUTER = "Outer"
    INNER = "Inner"
    BARRE = "Barre"


class RightHandStates(Enum):
    LOW = "0"
    END = "end"
    HIGH = "3"


def nested_dict():
    return defaultdict(nested_dict)


class BaseState():
    def __init__(self, instruments: Instruments):
        self.instruments: Instruments = instruments
        # 控制左手手掌位置和手臂ik的控制器,因为左手大拇指不参与演奏，所以也被归到这一类里
        self.left_hand_controllers = {
            "left_hand_controller": "H_L",
            "left_hand_ik_pivot_controller": "HP_L",
            "left_thumb_controller": "T_L",
            "left_thumb_ik_pivot_controller": "TP_L",
        }
        # 控制右手手掌位置和手臂ik的控制器，因为右手大拇指要参与演奏，所以不被归到这一类里
        self.right_hand_controllers = {
            "right_hand_controller": "H_R",
            "right_hand_ik_pivot_controller": "HP_R",
        }

        # 控制手掌旋转
        self.hand_rotation_controllers = {
            "left_hand_rotation_controller": "H_rotation_L",
            "right_hand_rotation_controller": "H_rotation_R"
        }
        # 控制左手手指位置
        self.left_finger_controllers = {
            "left_index_controller": "I_L",
            "left_middle_controller": "M_L",
            "left_ring_controller": "R_L",
            "left_little_controller": "P_L",
        }
        # 定义无效的组合
        self. invalid_combinations = {
            BasePositions.P0: [LeftHandStates.INNER],
            BasePositions.P2: [LeftHandStates.INNER],
            BasePositions.P1: [LeftHandStates.OUTER],
            BasePositions.P3: [LeftHandStates.OUTER]}
        # 控制右手手指位置
        self.right_finger_controllers = {
            "right_thumb_controller": "T_R",
            "right_thumb_ik_pivot_controller": "TP_R",
            "right_index_controller": "I_R",
            "right_middle_controller": "M_R",
            "right_ring_controller": "R_R",
            "right_little_controller": "P_R",
        } if instruments != Instruments.ELECTRIC_GUITAR else {
            "right_thumb_controller": "T_R",
        }

        self.guitar_fret_positions = {}
        for position in BasePositions:
            # 用于记录指板位置的四个基本点
            self.guitar_fret_positions[position.value] = f'Fret_{position.value}'

        # 用于记录左手位置的点
        self.left_hand_position_recorders = {}

        # 添加用于记录不同状态下左手位置的点
        for position in BasePositions:
            for state in LeftHandStates:
                # 跳过无效的组合
                if position in self.invalid_combinations and state in self.invalid_combinations[position]:
                    continue

                for left_controller in self.left_hand_controllers:
                    controller_name = self.left_hand_controllers[left_controller]
                    # 为每种有效的组合创建记录器
                    key = f'{state.name}_{position.value}_{controller_name}'.lower()
                    value = f'{state.value}_{position.value}_{controller_name}'
                    self.left_hand_position_recorders[key] = value

                for finger_controller in self.left_finger_controllers:
                    finger_name = self.left_finger_controllers[finger_controller]
                    key = f'{state.name}_{position.value}_{finger_name}'.lower()
                    value = f'{state.value}_{position.value}_{finger_name}'
                    self.left_hand_position_recorders[key] = value

        # 添加用于记录不同状态下左手旋转值的旋转记录器
        for position in BasePositions:
            for state in LeftHandStates:
                for hand_rotation_controller in self.hand_rotation_controllers:
                    hand_rotation_controller_name = self.hand_rotation_controllers[
                        hand_rotation_controller]
                    if hand_rotation_controller_name == 'H_rotation_R':
                        continue
                    # 跳过无效的组合
                    if position in self.invalid_combinations and state in self.invalid_combinations[position]:
                        continue

                    # 为每种有效的组合创建记录器
                    key = f'{state.name}_{position.value}_{hand_rotation_controller_name}'.lower(
                    )
                    value = f'{state.value}_{position.value}_{hand_rotation_controller_name}'
                    self.left_hand_position_recorders[key] = value

        # 用于记录右手位置的点
        self.right_hand_position_recorders = {}

        for right_hand_state in RightHandStates:
            self.right_hand_position_recorders[f'{right_hand_state}_h'] = f'Normal_P{right_hand_state.value}_H_R'
            self.right_hand_position_recorders[f'{right_hand_state}_hp'] = f'Normal_P{right_hand_state.value}_HP_R'
            # 电吉他只需要记录大拇指的3个位置，其它需要记录五个手指的位置
            self.right_hand_position_recorders[f'{right_hand_state}_p'] = f'p{right_hand_state.value}'
            # 这里是用西班牙吉他的缩写代表手指，指弹吉他和bass需要记录所有五个手指在三种状态下的位置
            # 为什么是使用的状态是3和0，这都是历史遗留问题
            if instruments != Instruments.ELECTRIC_GUITAR:
                self.right_hand_position_recorders[f'{right_hand_state}_tp'] = f'tp{right_hand_state.value}'
                for finger in ['i', 'm', 'a', 'ch']:
                    self.right_hand_position_recorders[f'{right_hand_state}_{finger}'] = f'{finger}{right_hand_state.value}'

        # 用于记录右手旋转值的旋转记录器
        self.right_hand_rotation_recorders = {}
        # 电吉他只需要记录一个旋转值
        self.right_hand_rotation_recorders['high'] = 'Normal_P3_H_rotation_R'
        self.right_hand_rotation_recorders['end'] = 'Normal_Pend_H_rotation_R'
        self.right_hand_rotation_recorders['low'] = 'Normal_P0_H_rotation_R'

        # 接下来是一些辅助线
        self.guidelines = {}

        # 吉他弦的振动方向
        self.guidelines['string_move_direction'] = 'string_move_direction'

        # 右手运动的辅助线
        if instruments == Instruments.ELECTRIC_GUITAR:
            # 电吉他演奏时的拨弦方向
            self.guidelines['left_thumb_move_direction'] = 'T_line'
        else:
            # 指弹吉它和bass演奏时要记录手背的朝向
            self.guidelines['left_hand_high_normal'] = 'right_hand_normal_p3'
            self.guidelines['left_hand_low_normal'] = 'right_hand_normal_p0'
            self.guidelines['thumb_direction_high'] = 'right_thumb_direct_p3'
            self.guidelines['thumb_direction_low'] = 'right_thumb_direct_p0'
            self.guidelines['finger_direction_high'] = 'right_finger_direct_p3'
            self.guidelines['finger_direction_low'] = 'right_finger_direct_p0'

    def add_controllers(self):
        """
        添加控制器对象到Blender场景中
        位置控制器使用立方体，旋转控制器使用正四面体
        """
        # 确保在对象模式下操作
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # 创建或获取主集合
        main_collection = self.get_or_create_collection("addons")

        # 创建控制器集合
        controllers_collection = self.get_or_create_collection(
            "Controllers", main_collection)

        # 创建左右手子集合
        left_hand_controller_collection = self.get_or_create_collection(
            "Left_Hand_Controllers", controllers_collection)
        right_hand_controller_collection = self.get_or_create_collection(
            "Right_Hand_Controllers", controllers_collection)

        # 添加左手控制器
        for controller_name, obj_name in self.left_hand_controllers.items():
            obj_type = "cone" if 'rotation' in controller_name else "cube"
            self.create_or_update_object(
                obj_name, obj_type, left_hand_controller_collection)

        # 添加右手控制器
        for controller_name, obj_name in self.right_hand_controllers.items():
            obj_type = "cone" if 'rotation' in controller_name else "cube"
            self.create_or_update_object(
                obj_name, obj_type, right_hand_controller_collection)

        # 添加左手手指控制器
        for controller_name, obj_name in self.left_finger_controllers.items():
            obj_type = "cone" if 'rotation' in controller_name else "cube"
            self.create_or_update_object(
                obj_name, obj_type, left_hand_controller_collection)

        # 添加右手手指控制器
        for controller_name, obj_name in self.right_finger_controllers.items():
            obj_type = "cone" if 'rotation' in controller_name else "cube"
            self.create_or_update_object(
                obj_name, obj_type, right_hand_controller_collection)

        # 添加手部旋转控制器
        for controller_name, obj_name in self.hand_rotation_controllers.items():
            obj_type = "cone" if 'rotation' in controller_name else "cube"
            # 根据名称判断是左手还是右手
            if '_L' in obj_name:
                self.create_or_update_object(
                    obj_name, obj_type, left_hand_controller_collection)
            else:
                self.create_or_update_object(
                    obj_name, obj_type, right_hand_controller_collection)

    def add_recorders(self):
        """
        添加记录器对象到Blender场景中
        位置记录器使用球体空物体，旋转记录器使用圆锥体空物体
        """
        # 确保在对象模式下操作
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT')

        # 创建或获取主集合
        main_collection = self.get_or_create_collection("addons")

        # 创建记录器集合
        recorders_collection = self.get_or_create_collection(
            "Recorders", main_collection)

        # 创建左右手子集合
        left_hand_recorder_collection = self.get_or_create_collection(
            "Left_Hand_Recorders", recorders_collection)
        right_hand_recorder_collection = self.get_or_create_collection(
            "Right_Hand_Recorders", recorders_collection)

        # 创建辅助线子集合
        guidelines_collection = self.get_or_create_collection(
            "Guidelines", recorders_collection)

        # 添加指板位置记录器
        for recorder_name, obj_name in self.guitar_fret_positions.items():
            self.create_or_update_object(
                obj_name, "sphere", left_hand_recorder_collection)

        # 添加左手位置记录器
        for recorder_name, obj_name in self.left_hand_position_recorders.items():
            obj_type = "cone_empty" if 'rotation' in recorder_name else "sphere"
            self.create_or_update_object(
                obj_name, obj_type, left_hand_recorder_collection)

        # 添加右手位置记录器
        for recorder_name, obj_name in self.right_hand_position_recorders.items():
            self.create_or_update_object(
                obj_name, "sphere", right_hand_recorder_collection)

        # 添加右手旋转记录器
        for recorder_name, obj_name in self.right_hand_rotation_recorders.items():
            self.create_or_update_object(
                obj_name, "cone_empty", right_hand_recorder_collection)

        # 添加辅助线对象
        for guideline_name, obj_name in self.guidelines.items():
            self.create_or_update_object(
                obj_name, "single_arrow", guidelines_collection)

    def get_or_create_collection(self, name, parent_collection=None):
        """
        获取或创建集合
        """
        if name in bpy.data.collections:
            collection = bpy.data.collections[name]
        else:
            collection = bpy.data.collections.new(name)
            if parent_collection:
                parent_collection.children.link(collection)
            else:
                # 如果没有指定父集合，链接到场景主集合
                bpy.context.scene.collection.children.link(collection)

        # 如果指定了父集合，则确保该集合在父集合中
        if parent_collection and collection.name not in [c.name for c in parent_collection.children]:
            parent_collection.children.link(collection)

        return collection

    def move_object_to_collection(self, obj, collection):
        """
        将对象移动到指定集合
        """
        # 从所有现有集合中移除对象
        for coll in obj.users_collection:
            coll.objects.unlink(obj)

        # 将对象链接到目标集合
        collection.objects.link(obj)

    def setup_all_objects(self):
        """
        一次性设置所有控制器和记录器
        """
        # 记录添加控件前addons集合及其子集合中的所有物体名称
        self.pre_obj_names = []
        if "addons" in bpy.data.collections:
            addons_collection = bpy.data.collections["addons"]
            # 收集addons集合及其所有子集合中的物体
            collections_to_check = [addons_collection]
            for coll in addons_collection.children_recursive:
                collections_to_check.append(coll)

            for coll in collections_to_check:
                for obj in coll.objects:
                    self.pre_obj_names.append(obj.name)

        # 添加控制器和记录器
        self.add_controllers()
        self.add_recorders()

        # 打印未使用的控件名称
        if self.pre_obj_names:
            print("\n未使用的控件:")
            for obj_name in self.pre_obj_names:
                print(f"  • {obj_name}")
        else:
            print("\n没有发现未使用的控件")

    def check_objects_status(self):
        """
        检查Blender中控制器和记录器的创建状态
        输出哪些对象已存在，哪些还不存在
        """
        print("=" * 50)
        print("控制器和记录器状态检查报告")
        print("=" * 50)

        # 检查控制器状态
        print("\n【控制器状态】")
        print("-" * 30)

        # 左手控制器
        print("\n左手控制器:")
        missing_left_ctrl = []
        existing_left_ctrl = []
        for controller_name, obj_name in self.left_hand_controllers.items():
            if obj_name in bpy.data.objects:
                existing_left_ctrl.append(obj_name)
                print(f"  ✓ {obj_name} (已存在)")
            else:
                missing_left_ctrl.append(obj_name)
                print(f"  ✗ {obj_name} (缺失)")

        # 右手控制器
        print("\n右手控制器:")
        missing_right_ctrl = []
        existing_right_ctrl = []
        for controller_name, obj_name in self.right_hand_controllers.items():
            if obj_name in bpy.data.objects:
                existing_right_ctrl.append(obj_name)
                print(f"  ✓ {obj_name} (已存在)")
            else:
                missing_right_ctrl.append(obj_name)
                print(f"  ✗ {obj_name} (缺失)")

        # 左手手指控制器
        print("\n左手手指控制器:")
        missing_left_finger_ctrl = []
        existing_left_finger_ctrl = []
        for controller_name, obj_name in self.left_finger_controllers.items():
            if obj_name in bpy.data.objects:
                existing_left_finger_ctrl.append(obj_name)
                print(f"  ✓ {obj_name} (已存在)")
            else:
                missing_left_finger_ctrl.append(obj_name)
                print(f"  ✗ {obj_name} (缺失)")

        # 右手手指控制器
        print("\n右手手指控制器:")
        missing_right_finger_ctrl = []
        existing_right_finger_ctrl = []
        for controller_name, obj_name in self.right_finger_controllers.items():
            if obj_name in bpy.data.objects:
                existing_right_finger_ctrl.append(obj_name)
                print(f"  ✓ {obj_name} (已存在)")
            else:
                missing_right_finger_ctrl.append(obj_name)
                print(f"  ✗ {obj_name} (缺失)")

        # 手部旋转控制器
        print("\n手部旋转控制器:")
        missing_hand_rot_ctrl = []
        existing_hand_rot_ctrl = []
        for controller_name, obj_name in self.hand_rotation_controllers.items():
            if obj_name in bpy.data.objects:
                existing_hand_rot_ctrl.append(obj_name)
                print(f"  ✓ {obj_name} (已存在)")
            else:
                missing_hand_rot_ctrl.append(obj_name)
                print(f"  ✗ {obj_name} (缺失)")

        # 检查记录器状态
        print("\n\n【记录器状态】")
        print("-" * 30)

        # 指板位置记录器
        print("\n指板位置记录器:")
        missing_fret_rec = []
        existing_fret_rec = []
        for recorder_name, obj_name in self.guitar_fret_positions.items():

            if obj_name in bpy.data.objects:
                existing_fret_rec.append(obj_name)
                print(f"  ✓ {obj_name} (已存在)")
            else:
                missing_fret_rec.append(obj_name)
                print(f"  ✗ {obj_name} (缺失)")

        # 左手位置记录器
        print("\n左手位置记录器:")
        missing_left_pos_rec = []
        existing_left_pos_rec = []
        for recorder_name, obj_name in self.left_hand_position_recorders.items():
            if obj_name in bpy.data.objects:
                existing_left_pos_rec.append(obj_name)
                print(f"  ✓ {obj_name} (已存在)")
            else:
                missing_left_pos_rec.append(obj_name)
                print(f"  ✗ {obj_name} (缺失)")

        # 右手位置记录器
        print("\n右手位置记录器:")
        missing_right_pos_rec = []
        existing_right_pos_rec = []
        for recorder_name, obj_name in self.right_hand_position_recorders.items():
            if obj_name in bpy.data.objects:
                existing_right_pos_rec.append(obj_name)
                print(f"  ✓ {obj_name} (已存在)")
            else:
                missing_right_pos_rec.append(obj_name)
                print(f"  ✗ {obj_name} (缺失)")

        # 右手旋转记录器
        print("\n右手旋转记录器:")
        missing_right_rot_rec = []
        existing_right_rot_rec = []
        for recorder_name, obj_name in self.right_hand_rotation_recorders.items():
            if obj_name in bpy.data.objects:
                existing_right_rot_rec.append(obj_name)
                print(f"  ✓ {obj_name} (已存在)")
            else:
                missing_right_rot_rec.append(obj_name)
                print(f"  ✗ {obj_name} (缺失)")

        # 辅助线
        print("\n辅助线:")
        missing_guidelines = []
        existing_guidelines = []
        for guideline_name, obj_name in self.guidelines.items():
            if obj_name in bpy.data.objects:
                existing_guidelines.append(obj_name)
                print(f"  ✓ {obj_name} (已存在)")
            else:
                missing_guidelines.append(obj_name)
                print(f"  ✗ {obj_name} (缺失)")

        # 统计信息
        print("\n\n【统计信息】")
        print("-" * 30)

        # 控制器统计
        total_ctrl = (len(self.left_hand_controllers) + len(self.right_hand_controllers) +
                      len(self.left_finger_controllers) + len(self.right_finger_controllers) +
                      len(self.hand_rotation_controllers))
        existing_ctrl = (len(existing_left_ctrl) + len(existing_right_ctrl) +
                         len(existing_left_finger_ctrl) + len(existing_right_finger_ctrl) +
                         len(existing_hand_rot_ctrl))
        missing_ctrl = (len(missing_left_ctrl) + len(missing_right_ctrl) +
                        len(missing_left_finger_ctrl) + len(missing_right_finger_ctrl) +
                        len(missing_hand_rot_ctrl))

        print(f"控制器总数: {total_ctrl}")
        print(f"已存在: {existing_ctrl}")
        print(f"缺失: {missing_ctrl}")

        # 记录器统计
        total_rec = (len(self.guitar_fret_positions) + len(self.left_hand_position_recorders) +
                     len(self.right_hand_position_recorders) + len(self.right_hand_rotation_recorders) +
                     len(self.guidelines))
        existing_rec = (len(existing_fret_rec) + len(existing_left_pos_rec) +
                        len(existing_right_pos_rec) + len(existing_right_rot_rec) +
                        len(existing_guidelines))
        missing_rec = (len(missing_fret_rec) + len(missing_left_pos_rec) +
                       len(missing_right_pos_rec) + len(missing_right_rot_rec) +
                       len(missing_guidelines))

        print(f"记录器总数: {total_rec}")
        print(f"已存在: {existing_rec}")
        print(f"缺失: {missing_rec}")

        total_objects = total_ctrl + total_rec
        total_existing = existing_ctrl + existing_rec
        total_missing = missing_ctrl + missing_rec

        print(f"\n对象总计: {total_objects}")
        print(f"已存在总计: {total_existing}")
        print(f"缺失总计: {total_missing}")
        print(
            f"完成度: {total_existing/total_objects*100:.1f}%" if total_objects > 0 else "完成度: 0%")

        # 详细缺失列表
        if total_missing > 0:
            print("\n\n【缺失对象详细列表】")
            print("-" * 30)
            if missing_ctrl > 0:
                print("\n缺失的控制器:")
                for obj_name in (missing_left_ctrl + missing_right_ctrl +
                                 missing_left_finger_ctrl + missing_right_finger_ctrl +
                                 missing_hand_rot_ctrl):
                    print(f"  • {obj_name}")

            if missing_rec > 0:
                print("\n缺失的记录器:")
                for obj_name in (missing_fret_rec + missing_left_pos_rec +
                                 missing_right_pos_rec + missing_right_rot_rec +
                                 missing_guidelines):
                    print(f"  • {obj_name}")

        print("\n" + "=" * 50)
        print("检查完成")
        print("=" * 50)

        return {
            'controllers': {
                'existing': existing_ctrl,
                'missing': missing_ctrl,
                'total': total_ctrl
            },
            'recorders': {
                'existing': existing_rec,
                'missing': missing_rec,
                'total': total_rec
            },
            'overall': {
                'existing': total_existing,
                'missing': total_missing,
                'total': total_objects
            }
        }

    def create_or_update_object(self, obj_name, obj_type="cube", collection=None, rotation_mode='QUATERNION'):
        """
        创建或更新物体的通用方法

        :param obj_name: 物体名称
        :param obj_type: 物体类型 ("cube", "cone", "sphere", "single_arrow")
        :param collection: 物体所属集合
        :param rotation_mode: 旋转模式，默认为四元数
        :return: 物体对象
        """
        # 从pre_obj_names中移除同名物体
        if hasattr(self, 'pre_obj_names') and obj_name in self.pre_obj_names:
            self.pre_obj_names.remove(obj_name)

        # 如果物体已存在
        if obj_name in bpy.data.objects:
            obj = bpy.data.objects[obj_name]
            # 将物体移动到指定集合
            if collection and obj.name not in collection.objects:
                self.move_object_to_collection(obj, collection)
            # 直接返回
            return bpy.data.objects[obj_name]

        # 根据类型创建不同的物体
        if obj_type == "cube":
            bpy.ops.mesh.primitive_cube_add(
                size=0.2, enter_editmode=False, align='WORLD', location=(0, 0, 0), scale=(0.1, 0.1, 0.1))
        elif obj_type == "cone":
            bpy.ops.mesh.primitive_cone_add(enter_editmode=False, align='WORLD', location=(
                0, 0, 0), scale=(0.01, 0.01, 0.01))
        elif obj_type == "sphere":
            bpy.ops.object.empty_add(type='SPHERE', radius=0.01)
        elif obj_type == "cone_empty":
            bpy.ops.object.empty_add(type='CONE', radius=0.01)
        elif obj_type == "single_arrow":
            bpy.ops.object.empty_add(type='SINGLE_ARROW', radius=1.0)

        # 设置物体名称
        obj = bpy.context.active_object
        obj.name = obj_name

        # 设置旋转模式（如果适用）
        if obj_type in ["cone", "cone_empty"] or (hasattr(obj, 'rotation_mode') and rotation_mode):
            obj.rotation_mode = rotation_mode

        # 将物体移动到指定集合
        if collection:
            self.move_object_to_collection(obj, collection)

        return obj

    def copy_transfer(self, source_obj, target_obj, direction: str = "set", transfer_type: str = "location"):
        """
        在两个对象之间传输数据的通用方法

        :param source_obj: 源对象
        :param target_obj: 目标对象
        :param direction: 传输方向，"set"表示控制器到记录器，"load"表示记录器到控制器
        :param transfer_type: 传输类型，"location"表示位置，"rotation"表示旋转
        """
        if transfer_type == "location":
            if direction == "set":
                # 解锁记录器位置
                self.unlock_object_location(target_obj)
            # 复制位置
            target_obj.location = source_obj.location
        elif transfer_type == "rotation":
            if direction == "set":
                # 解锁记录器旋转
                self.unlock_object_rotation(target_obj)

            # 复制旋转值
            if source_obj.rotation_mode == target_obj.rotation_mode:
                if source_obj.rotation_mode == 'QUATERNION':
                    target_obj.rotation_quaternion = source_obj.rotation_quaternion
                else:
                    target_obj.rotation_euler = source_obj.rotation_euler
            else:
                # 如果旋转模式不同，先将目标对象的旋转模式设置为与源对象相同
                target_obj.rotation_mode = source_obj.rotation_mode
                # 然后复制旋转值
                if source_obj.rotation_mode == 'QUATERNION':
                    target_obj.rotation_quaternion = source_obj.rotation_quaternion
                else:
                    target_obj.rotation_euler = source_obj.rotation_euler

    def transfer_left_hand_state(self, base_position: BasePositions, left_hand_state: LeftHandStates, direction: str = "set"):
        """
        在左手控制器和记录器之间传输状态数据

        :param base_position: 基础位置 (P0, P1, P2, P3)
        :param left_hand_state: 左手状态 (NORMAL, OUTER, INNER, BARRE)
        :param direction: 传输方向，"set"表示控制器到记录器，"load"表示记录器到控制器
        """
        if direction == "set":
            print(
                f"设置左手位置: {base_position.value}, 状态: {left_hand_state.value}")
            source_suffix = "控制器"
            target_suffix = "记录器"
        else:
            print(
                f"加载左手位置: {base_position.value}, 状态: {left_hand_state.value}")
            source_suffix = "记录器"
            target_suffix = "控制器"

        # 检查提供的组合是否有效
        if base_position in self.invalid_combinations and left_hand_state in self.invalid_combinations[base_position]:
            print(f"警告: {base_position.value} 位置不支持 {left_hand_state.value} 状态")
            return False

        # 处理手指控制器（位置和旋转）
        print(f"\n传输手指控制器{source_suffix}到{target_suffix}:")
        for controller_name, obj_name in self.left_finger_controllers.items():
            # 处理位置数据
            position_recorder_key = f'{left_hand_state.name}_{base_position.value}_{obj_name}'.lower(
            )

            if position_recorder_key in self.left_hand_position_recorders:
                position_recorder_name = self.left_hand_position_recorders[position_recorder_key]
                if position_recorder_name in bpy.data.objects and obj_name in bpy.data.objects:
                    source_obj = bpy.data.objects[obj_name] if direction == "set" else bpy.data.objects[position_recorder_name]
                    target_obj = bpy.data.objects[position_recorder_name] if direction == "set" else bpy.data.objects[obj_name]

                    # 使用通用方法复制位置
                    self.copy_transfer(source_obj, target_obj,
                                       direction, "location")
                    print(f"  ✓ 位置 {obj_name} -> {position_recorder_name}" if direction ==
                          "set" else f"  ✓ 位置 {position_recorder_name} -> {obj_name}")
                else:
                    print(f"  ✗ 跳过位置 {position_recorder_key}: 对象不存在")
            else:
                print(f"  ✗ 未找到位置记录器键: {position_recorder_key}")

        # 处理手部旋转控制器
        print(f"\n传输手部旋转控制器{source_suffix}到{target_suffix}:")
        for controller_name, obj_name in self.hand_rotation_controllers.items():
            # 只处理左手旋转控制器
            if '_L' in obj_name:
                # 构造记录器名称
                rotation_recorder_key = f'{left_hand_state.name}_{base_position.value}_{obj_name}'.lower(
                )

                # 检查记录器是否存在
                if rotation_recorder_key in self.left_hand_position_recorders:
                    rotation_recorder_name = self.left_hand_position_recorders[rotation_recorder_key]
                    if rotation_recorder_name in bpy.data.objects and obj_name in bpy.data.objects:
                        source_obj = bpy.data.objects[obj_name] if direction == "set" else bpy.data.objects[rotation_recorder_name]
                        target_obj = bpy.data.objects[rotation_recorder_name] if direction == "set" else bpy.data.objects[obj_name]

                        # 使用通用方法复制旋转
                        self.copy_transfer(
                            source_obj, target_obj, direction, "rotation")
                        print(f"  ✓ 旋转 {obj_name} -> {rotation_recorder_name}" if direction ==
                              "set" else f"  ✓ 旋转 {rotation_recorder_name} -> {obj_name}")
                    else:
                        print(f"  ✗ 跳过旋转 {rotation_recorder_key}: 对象不存在")
                else:
                    print(f"  ✗ 未找到旋转记录器键: {rotation_recorder_key}")

        # 处理左手手掌控制器（位置和旋转）
        print(f"\n传输左手手掌控制器{source_suffix}到{target_suffix}:")
        for controller_name, obj_name in self.left_hand_controllers.items():
            # 处理位置数据
            position_recorder_key = f'{left_hand_state.name}_{base_position.value}_{obj_name}'.lower(
            )

            if position_recorder_key in self.left_hand_position_recorders:
                position_recorder_name = self.left_hand_position_recorders[position_recorder_key]
                if position_recorder_name in bpy.data.objects and obj_name in bpy.data.objects:
                    source_obj = bpy.data.objects[obj_name] if direction == "set" else bpy.data.objects[position_recorder_name]
                    target_obj = bpy.data.objects[position_recorder_name] if direction == "set" else bpy.data.objects[obj_name]

                    # 使用通用方法复制位置
                    self.copy_transfer(source_obj, target_obj,
                                       direction, "location")
                    print(f"  ✓ 位置 {obj_name} -> {position_recorder_name}" if direction ==
                          "set" else f"  ✓ 位置 {position_recorder_name} -> {obj_name}")
                else:
                    print(f"  ✗ 跳过位置 {position_recorder_key}: 对象不存在")
            else:
                print(f"  ✗ 未找到位置记录器键: {position_recorder_key}")

            # 处理旋转数据
            rotation_recorder_key = f'{left_hand_state.name}_{base_position.value}_{obj_name}'.lower(
            )
            if rotation_recorder_key in self.left_hand_position_recorders:
                rotation_recorder_name = self.left_hand_position_recorders[rotation_recorder_key]
                if rotation_recorder_name in bpy.data.objects and obj_name in bpy.data.objects:
                    source_obj = bpy.data.objects[obj_name] if direction == "set" else bpy.data.objects[rotation_recorder_name]
                    target_obj = bpy.data.objects[rotation_recorder_name] if direction == "set" else bpy.data.objects[obj_name]

                    # 使用通用方法复制旋转
                    self.copy_transfer(source_obj, target_obj,
                                       direction, "rotation")
                    print(f"  ✓ 旋转 {obj_name} -> {rotation_recorder_name}" if direction ==
                          "set" else f"  ✓ 旋转 {rotation_recorder_name} -> {obj_name}")
                else:
                    print(f"  ✗ 跳过旋转 {rotation_recorder_key}: 对象不存在")
            else:
                print(f"  ✗ 未找到旋转记录器键: {rotation_recorder_key}")

        print(
            f"\n左手{('设置' if direction == 'set' else '加载')}完成: {base_position.value} + {left_hand_state.value}")
        return True

    def transfer_right_hand_state(self, right_hand_state: RightHandStates, direction: str = "set"):
        """
        在右手控制器和记录器之间传输状态数据

        :param right_hand_state: 右手状态 (LOW, END, HIGH)
        :param direction: 传输方向，"set"表示控制器到记录器，"load"表示记录器到控制器
        """
        print("---------------------------------------------------")
        if direction == "set":
            print(f"设置右手位置: {right_hand_state}")
            source_suffix = "控制器"
            target_suffix = "记录器"
        else:
            print(f"加载右手位置: {right_hand_state}")
            source_suffix = "记录器"
            target_suffix = "控制器"

        # 建立西班牙记指法到英文控制器的映射
        finger_mapping = {
            'p': 'T_R',   # 拇指
            'tp': 'TP_R',  # 拇指ik pivot
            'i': 'I_R',   # 食指
            'm': 'M_R',   # 中指
            'a': 'R_R',   # 无名指
            'ch': 'P_R'   # 小指
        }

        current_fingers = ['p'] if self.instruments == Instruments.ELECTRIC_GUITAR else [
            'p', 'i', 'm', 'a', 'ch', 'tp']

        # 处理所有手指控制器（位置和旋转）
        print(f"\n传输右手手指控制器{source_suffix}到{target_suffix}:")
        for finger_spanish, finger_english in finger_mapping.items():
            if finger_spanish not in current_fingers:
                continue

            # 处理位置数据
            position_recorder_key = f'{right_hand_state}_{finger_spanish}'
            if position_recorder_key in self.right_hand_position_recorders:
                position_recorder_name = self.right_hand_position_recorders[position_recorder_key]
                if position_recorder_name in bpy.data.objects and finger_english in bpy.data.objects:
                    source_obj = bpy.data.objects[finger_english] if direction == "set" else bpy.data.objects[position_recorder_name]
                    target_obj = bpy.data.objects[position_recorder_name] if direction == "set" else bpy.data.objects[finger_english]

                    # 使用通用方法复制位置
                    self.copy_transfer(source_obj, target_obj,
                                       direction, "location")
                    print(f"  ✓ 位置 {finger_english} -> {position_recorder_name}" if direction ==
                          "set" else f"  ✓ 位置 {position_recorder_name} -> {finger_english}")
                else:
                    print(f"  ✗ 跳过位置 {position_recorder_key}: 对象不存在")
            else:
                print(f"  ✗ 未找到位置记录器键: {position_recorder_key}")

        # 处理右手旋转控制器
        print(f"\n传输右手旋转控制器{source_suffix}到{target_suffix}:")
        for controller_name, obj_name in self.hand_rotation_controllers.items():
            # 只处理右手旋转控制器
            if '_R' in obj_name:
                # 构造记录器名称，根据right_hand_state映射到对应的记录器
                recorder_key_map = {
                    RightHandStates.LOW: 'low',
                    RightHandStates.END: 'end',
                    RightHandStates.HIGH: 'high'
                }

                if right_hand_state in recorder_key_map:
                    recorder_key = recorder_key_map[right_hand_state]

                    # 检查记录器是否存在
                    if recorder_key in self.right_hand_rotation_recorders:
                        recorder_name = self.right_hand_rotation_recorders[recorder_key]
                        if recorder_name in bpy.data.objects and obj_name in bpy.data.objects:
                            source_obj = bpy.data.objects[obj_name] if direction == "set" else bpy.data.objects[recorder_name]
                            target_obj = bpy.data.objects[recorder_name] if direction == "set" else bpy.data.objects[obj_name]

                            # 使用通用方法复制旋转
                            self.copy_transfer(
                                source_obj, target_obj, direction, "rotation")
                            print(f"  ✓ 旋转 {obj_name} -> {recorder_name}" if direction ==
                                  "set" else f"  ✓ 旋转 {recorder_name} -> {obj_name}")
                        else:
                            print(f"  ✗ 跳过旋转 {recorder_key}: 对象不存在")
                    else:
                        print(f"  ✗ 未找到记录器键: {recorder_key}")
                else:
                    print(f"  ✗ 未定义 {right_hand_state} 的旋转记录器映射")

        # 处理右手手掌控制器（位置和旋转）
        print(f"\n传输右手手掌控制器{source_suffix}到{target_suffix}:")
        for controller_name, obj_name in self.right_hand_controllers.items():
            # 处理位置数据
            position_recorder_key = f'{right_hand_state}_h' if obj_name == "H_R" else f'{right_hand_state}_hp'
            if position_recorder_key in self.right_hand_position_recorders:
                position_recorder_name = self.right_hand_position_recorders[position_recorder_key]
                if position_recorder_name in bpy.data.objects and obj_name in bpy.data.objects:
                    source_obj = bpy.data.objects[obj_name] if direction == "set" else bpy.data.objects[position_recorder_name]
                    target_obj = bpy.data.objects[position_recorder_name] if direction == "set" else bpy.data.objects[obj_name]

                    # 使用通用方法复制位置
                    self.copy_transfer(source_obj, target_obj,
                                       direction, "location")
                    print(f"  ✓ 位置 {obj_name} -> {position_recorder_name}" if direction ==
                          "set" else f"  ✓ 位置 {position_recorder_name} -> {obj_name}")
                else:
                    print(f"  ✗ 跳过位置 {position_recorder_key}: 对象不存在")
            else:
                print(f"  ✗ 未找到位置记录器键: {position_recorder_key}")

            # 处理旋转数据 - 只处理 H_rotation_R 控制器的旋转
            if obj_name == "H_rotation_R":  # 只有 H_R 控制器需要记录旋转值
                # 构造记录器名称，根据right_hand_state映射到对应的记录器
                recorder_key_map = {
                    RightHandStates.LOW: 'low',
                    RightHandStates.END: 'end',
                    RightHandStates.HIGH: 'high'
                }

                if right_hand_state in recorder_key_map:
                    rotation_recorder_key = recorder_key_map[right_hand_state]
                    if rotation_recorder_key in self.right_hand_rotation_recorders:
                        rotation_recorder_name = self.right_hand_rotation_recorders[
                            rotation_recorder_key]
                        if rotation_recorder_name in bpy.data.objects and obj_name in bpy.data.objects:
                            source_obj = bpy.data.objects[obj_name] if direction == "set" else bpy.data.objects[rotation_recorder_name]
                            target_obj = bpy.data.objects[rotation_recorder_name] if direction == "set" else bpy.data.objects[obj_name]

                            # 使用通用方法复制旋转
                            self.copy_transfer(
                                source_obj, target_obj, direction, "rotation")
                            print(f"  ✓ 旋转 {obj_name} -> {rotation_recorder_name}" if direction ==
                                  "set" else f"  ✓ 旋转 {rotation_recorder_name} -> {obj_name}")
                        else:
                            print(f"  ✗ 跳过旋转 {rotation_recorder_key}: 对象不存在")
                    else:
                        print(f"  ✗ 未找到旋转记录器键: {rotation_recorder_key}")
                else:
                    print(f"  ✗ 未定义 {right_hand_state} 的旋转记录器映射")

        print(
            f"\n右手{('设置' if direction == 'set' else '加载')}完成: {right_hand_state.value}")
        return True

    def unlock_object_location(self, obj):
        """
        解锁对象的位置锁定
        """
        obj.lock_location[0] = False  # X
        obj.lock_location[1] = False  # Y
        obj.lock_location[2] = False  # Z

    def unlock_object_rotation(self, obj):
        """
        解锁对象的旋转锁定
        """
        obj.lock_rotation[0] = False  # X
        obj.lock_rotation[1] = False  # Y
        obj.lock_rotation[2] = False  # Z

    def export_controller_info(self, file_name: str) -> None:
        """
        :param file_name: 输出文件名
        usage:这个方法用于将所有控制器的位置和旋转信息输出到json文件
        """

        result = nested_dict()

        # 导出左手手指位置控制器信息
        print("导出左手手指位置控制器信息...")
        for recorder_key, recorder_name in self.left_hand_position_recorders.items():
            if recorder_name in bpy.data.objects and not 'rotation' in recorder_key:
                obj = bpy.data.objects[recorder_name]

                # 解析记录器键名来确定分类
                if recorder_key.startswith('barre_'):
                    # 横按状态
                    parts = recorder_key.split('_')
                    if len(parts) >= 3:
                        position_name = f"{parts[1].upper()}"
                        controller_name = f'{parts[2]}_{parts[3]}'
                        controller_name = controller_name.upper()
                        # 查找对应的控制器名称
                        for ctrl_key, ctrl_name in self.left_hand_controllers.items():
                            if ctrl_name == controller_name:
                                controller_name = ctrl_name
                                break
                        result['BARRE_LEFT_HAND_POSITIONS'][position_name][controller_name] = obj.location
                else:
                    # 其他状态 (Normal, Outer, Inner)
                    parts = recorder_key.split('_')
                    if len(parts) >= 4:
                        state_name = parts[0]
                        position_name = parts[1].upper()
                        controller_name = parts[2] + '_' + parts[3]  # 例如 H_L
                        controller_name = controller_name.upper()

                        if state_name == 'normal':
                            result['NORMAL_LEFT_HAND_POSITIONS'][position_name][controller_name] = obj.location
                        elif state_name == 'outer':
                            result['OUTER_LEFT_HAND_POSITIONS'][position_name][controller_name] = obj.location
                        elif state_name == 'inner':
                            result['INNER_LEFT_HAND_POSITIONS'][position_name][controller_name] = obj.location

        # 导出指板位置记录器信息
        print("导出指板位置记录器信息...")
        for position_enum, recorder_name in self.guitar_fret_positions.items():
            if recorder_name in bpy.data.objects:
                obj = bpy.data.objects[recorder_name]
                position_name = position_enum
                parts = recorder_name.split('_')
                if len(parts) >= 3:
                    position_name = parts[1].capitalize(
                    ) + "_" + parts[2].upper()
                result['LEFT_FINGER_POSITIONS'][position_name] = obj.location

        # 导出旋转控制器信息
        print("导出旋转控制器信息...")
        for recorder_key, recorder_name in self.left_hand_position_recorders.items():
            if recorder_name in bpy.data.objects and 'rotation' in recorder_key:
                obj = bpy.data.objects[recorder_name]

                # 解析记录器键名
                parts = recorder_key.split('_')
                if len(parts) >= 4:
                    state_name = parts[0].capitalize()
                    position_name = parts[1].capitalize()
                    controller_name = parts[2].upper() + \
                        '_' + parts[3] + '_' + \
                        parts[4].upper()  # 例如 H_rotation_L

                    # 统一转换为四元数保存
                    if obj.rotation_mode == 'QUATERNION':
                        result['ROTATIONS'][controller_name][state_name][position_name] = obj.rotation_quaternion
                    else:
                        result['ROTATIONS'][controller_name][state_name][position_name] = obj.rotation_euler

        # 导出右手位置控制器信息
        print("导出右手位置控制器信息...")
        for recorder_key, recorder_name in self.right_hand_position_recorders.items():
            if recorder_name in bpy.data.objects:
                obj = bpy.data.objects[recorder_name]
                result['RIGHT_HAND_POSITIONS'][recorder_name] = obj.location

        # 导出右手旋转控制器信息
        print("导出右手旋转控制器信息...")
        for recorder_key, recorder_name in self.right_hand_rotation_recorders.items():
            if recorder_name in bpy.data.objects:
                obj = bpy.data.objects[recorder_name]

                # 解析记录器键名
                parts = recorder_name.split('_')
                position_name = parts[1]

                # 统一转换为四元数保存
                if obj.rotation_mode == 'QUATERNION':
                    result['ROTATIONS']['H_rotation_R']['Normal'][position_name] = obj.rotation_quaternion
                else:
                    result['ROTATIONS']['H_rotation_R']['Normal'][position_name] = obj.rotation_euler

        # 导出辅助线信息
        print("导出辅助线信息...")
        for guideline_key, guideline_name in self.guidelines.items():
            if guideline_name in bpy.data.objects:
                obj = bpy.data.objects[guideline_name]

                # 获取四元数并转换为方向向量
                obj_quaternion_normalized = obj.rotation_quaternion.normalized()
                rot_matrix = obj_quaternion_normalized.to_matrix()
                vec = rot_matrix @ mathutils.Vector((0, 0, 1))

                result['RIGHT_HAND_LINES'][guideline_name]['vector'] = vec
                result['RIGHT_HAND_LINES'][guideline_name]['location'] = obj.location

        # 写入文件
        data = json.dumps(result, default=list, indent=4)

        with open(file_name, 'w') as f:
            f.write(data)
            print(f'控制器信息已导出到 {file_name}')

    def import_controller_info(self, file_name: str) -> None:
        """
        :param file_name: 输入文件名
        :usage: 这个方法用于将所有控制器的位置和旋转信息从json文件导入
        """
        try:
            # 检查文件是否存在

            if not os.path.exists(file_name):
                raise FileNotFoundError(f"找不到文件: {file_name}")

            result = nested_dict()

            # 尝试加载JSON文件
            with open(file_name, 'r', encoding='utf-8') as f:
                try:
                    result = json.load(f)
                except json.JSONDecodeError as e:
                    raise ValueError(f"JSON文件格式错误: {e}")

            loaded_info = []  # 用于记录成功加载的信息

            # 导入左手手指位置控制器信息
            print("导入左手手指位置控制器信息...")
            left_hand_loaded = 0
            for recorder_key, recorder_name in self.left_hand_position_recorders.items():
                if recorder_name in bpy.data.objects and 'rotation' not in recorder_key:
                    try:
                        obj = bpy.data.objects[recorder_name]

                        # 解析记录器键名来确定分类
                        if recorder_key.startswith('barre_'):
                            # 横按状态
                            parts = recorder_key.split('_')
                            if len(parts) >= 3:
                                position_name = f"{parts[1].upper()}"
                                controller_name = f'{parts[2]}_{parts[3]}'
                                controller_name = controller_name.upper()
                                # 查找对应的控制器名称
                                for ctrl_key, ctrl_name in self.left_hand_controllers.items():
                                    if ctrl_name == controller_name:
                                        controller_name = ctrl_name
                                        break
                                obj.location = result['BARRE_LEFT_HAND_POSITIONS'][position_name][controller_name]
                                left_hand_loaded += 1
                        else:
                            # 其他状态 (Normal, Outer, Inner)
                            parts = recorder_key.split('_')
                            if len(parts) >= 4:
                                state_name = parts[0]
                                position_name = parts[1].upper()
                                controller_name = parts[2] + \
                                    '_' + parts[3]  # 例如 H_L
                                controller_name = controller_name.upper()

                                if state_name == 'normal':
                                    obj.location = result['NORMAL_LEFT_HAND_POSITIONS'][position_name][controller_name]
                                elif state_name == 'outer':
                                    obj.location = result['OUTER_LEFT_HAND_POSITIONS'][position_name][controller_name]
                                elif state_name == 'inner':
                                    obj.location = result['INNER_LEFT_HAND_POSITIONS'][position_name][controller_name]
                                left_hand_loaded += 1
                    except KeyError as e:
                        print(f"警告: 缺少左手位置数据键 {e}，跳过 {recorder_name}")
                    except Exception as e:
                        print(f"警告: 导入左手位置 {recorder_name} 时出错: {e}")

            loaded_info.append(f"左手手指位置控制器: {left_hand_loaded} 个")

            # 导入指板位置记录器信息
            print("导入指板位置记录器信息...")
            fret_loaded = 0
            for position_enum, recorder_name in self.guitar_fret_positions.items():
                if recorder_name in bpy.data.objects:
                    try:
                        obj = bpy.data.objects[recorder_name]
                        position_name = position_enum
                        parts = recorder_name.split('_')
                        if len(parts) >= 3:
                            position_name = parts[1].capitalize(
                            ) + "_" + parts[2].upper()
                        obj.location = result['LEFT_FINGER_POSITIONS'][position_name]
                        fret_loaded += 1
                    except KeyError as e:
                        print(f"警告: 缺少指板位置数据键 {e}，跳过 {recorder_name}")
                    except Exception as e:
                        print(f"警告: 导入指板位置 {recorder_name} 时出错: {e}")

            loaded_info.append(f"指板位置记录器: {fret_loaded} 个")

            # 导入旋转控制器信息
            print("导入旋转控制器信息...")
            rotation_loaded = 0
            for recorder_key, recorder_name in self.left_hand_position_recorders.items():
                if recorder_name in bpy.data.objects and 'rotation' in recorder_key:
                    try:
                        obj = bpy.data.objects[recorder_name]

                        # 解析记录器键名
                        parts = recorder_key.split('_')
                        if len(parts) >= 4:
                            state_name = parts[0].capitalize()
                            position_name = parts[1].capitalize()
                            controller_name = parts[2].upper(
                            ) + '_' + parts[3] + '_' + parts[4].upper()  # 例如 H_rotation_L

                            # 统一转换为四元数保存
                            if obj.rotation_mode == 'QUATERNION':
                                obj.rotation_quaternion = result['ROTATIONS'][controller_name][state_name][position_name]
                            else:
                                obj.rotation_euler = result['ROTATIONS'][controller_name][state_name][position_name]
                            rotation_loaded += 1
                    except KeyError as e:
                        print(f"警告: 缺少旋转数据键 {e}，跳过 {recorder_name}")
                    except Exception as e:
                        print(f"警告: 导入旋转 {recorder_name} 时出错: {e}")

            loaded_info.append(f"左手旋转控制器: {rotation_loaded} 个")

            # 导入右手位置控制器信息
            print("导入右手位置控制器信息...")
            right_hand_loaded = 0
            for recorder_key, recorder_name in self.right_hand_position_recorders.items():
                if recorder_name in bpy.data.objects:
                    try:
                        obj = bpy.data.objects[recorder_name]
                        obj.location = result['RIGHT_HAND_POSITIONS'][recorder_name]
                        right_hand_loaded += 1
                    except KeyError as e:
                        print(f"警告: 缺少右手位置数据键 {e}，跳过 {recorder_name}")
                    except Exception as e:
                        print(f"警告: 导入右手位置 {recorder_name} 时出错: {e}")

            loaded_info.append(f"右手位置控制器: {right_hand_loaded} 个")

            # 导入右手旋转控制器信息
            print("导入右手旋转控制器信息...")
            right_rotation_loaded = 0
            for recorder_key, recorder_name in self.right_hand_rotation_recorders.items():
                if recorder_name in bpy.data.objects:
                    try:
                        obj = bpy.data.objects[recorder_name]

                        # 解析记录器键名
                        parts = recorder_name.split('_')
                        position_name = parts[1]

                        # 统一转换为四元数保存
                        if obj.rotation_mode == 'QUATERNION':
                            obj.rotation_quaternion = result['ROTATIONS']['H_rotation_R']['Normal'][position_name]
                        else:
                            obj.rotation_euler = result['ROTATIONS']['H_rotation_R']['Normal'][position_name]
                        right_rotation_loaded += 1
                    except KeyError as e:
                        print(f"警告: 缺少右手旋转数据键 {e}，跳过 {recorder_name}")
                    except Exception as e:
                        print(f"警告: 导入右手旋转 {recorder_name} 时出错: {e}")

            loaded_info.append(f"右手旋转控制器: {right_rotation_loaded} 个")

            # 导入辅助线信息
            print("导入辅助线信息...")
            guideline_loaded = 0
            for guideline_key, guideline_name in self.guidelines.items():
                if guideline_name in bpy.data.objects:
                    try:
                        obj = bpy.data.objects[guideline_name]
                        obj.location = result['RIGHT_HAND_LINES'][guideline_name]['location']
                        guideline_loaded += 1
                    except KeyError as e:
                        print(f"警告: 缺少辅助线数据键 {e}，跳过 {guideline_name}")
                    except Exception as e:
                        print(f"警告: 导入辅助线 {guideline_name} 时出错: {e}")

            loaded_info.append(f"辅助线: {guideline_loaded} 个")

            # 成功加载通知
            print("\n" + "="*50)
            print("控制器信息导入成功!")
            print("="*50)
            for info in loaded_info:
                print(f"  • {info}")
            print("="*50)

        except FileNotFoundError as e:
            print(f"错误: {e}")
        except ValueError as e:
            print(f"错误: {e}")
        except Exception as e:
            print(f"导入控制器信息时发生未知错误: {e}")
            import traceback
            traceback.print_exc()


if __name__ == '__main__':
    # 创建一个实例
    base_state = BaseState(Instruments.FINGER_STYLE_GUITAR)
    # 检测缺失控件状态
    base_state.check_objects_status()
    # 初始化所有控件，运行一次就可以了，以后可以注释掉
    base_state.setup_all_objects()

    # 保存或者加载当前状态，注释掉不用的代码就可以切换
    direction = 'set'
#    direction = 'load'

    # 手动选择左手状态
    base_position: BasePositions = BasePositions.P1
    left_hand_state: LeftHandStates = LeftHandStates.NORMAL

    base_state.transfer_left_hand_state(
        base_position, left_hand_state, direction=direction)

    # 手动选择右手状态
    right_hand_state: RightHandStates = RightHandStates.HIGH

    base_state.transfer_right_hand_state(
        right_hand_state, direction=direction)

    file_name = 'Jeht.json'
    file_path = f'G:/fretDance/asset/controller_infos/{file_name}'

    # 全都设置好以后，导出控件信息
    base_state.export_controller_info(file_path)
