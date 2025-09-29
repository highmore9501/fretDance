# g:\fretDance\src\blender\__init__.py
import os
import json
import bpy  # type: ignore
from bpy.types import Panel, Operator  # type: ignore
from bpy.props import EnumProperty, StringProperty  # type: ignore
from bpy_extras.io_utils import ImportHelper, ExportHelper  # type: ignore
from .make_animation import clear_all_keyframe, clear_string_aniamtion, animate_hand, animate_string

# 使用相对导入
from .base_states import BaseState, Instruments, BasePositions, LeftHandStates, RightHandStates
from .mmd2blender import mmd2blender

bl_info = {
    "name": "FretDance Controller Setup",
    "author": "BigHippo78",
    "version": (1, 0),
    "blender": (4, 5, 0),
    "location": "3D View > Sidebar > FretDance",
    "description": "Setup and check guitar controller objects for animation",
    "category": "Animation",
}


class FRET_DANCE_OT_setup_objects(Operator):
    """Setup all controller and recorder objects"""
    bl_idname = "fret_dance.setup_objects"
    bl_label = "设置控制与记录器"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        base_state = BaseState(Instruments(int(scene.fret_dance_instruments)))
        base_state.setup_all_objects()
        self.report({'INFO'}, "All objects have been setup")
        return {'FINISHED'}


class FRET_DANCE_OT_check_status(Operator):
    """Check the status of controller and recorder objects"""
    bl_idname = "fret_dance.check_status"
    bl_label = "检查状态"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        base_state = BaseState(Instruments(int(scene.fret_dance_instruments)))
        base_state.check_objects_status()
        self.report({'INFO'}, "Check complete. See console for details.")
        return {'FINISHED'}


class WM_OT_mmd2blender_initialize(bpy.types.Operator):
    """初始化MMD骨骼"""
    bl_idname = "wm.mmd2blender_initialize"
    bl_label = "初始化MMD骨骼"
    bl_description = "初始化MMD骨骼以适配Blender"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        try:
            # 调用mmd2blender方法
            mmd2blender()
            self.report({'INFO'}, "MMD骨骼初始化完成")
        except Exception as e:
            self.report({'ERROR'}, f"初始化失败: {str(e)}")
            return {'CANCELLED'}
        return {'FINISHED'}


class FRET_DANCE_OT_set_state(Operator):
    """Set hand states from controllers to recorders"""
    bl_idname = "fret_dance.set_state"
    bl_label = "Set"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        base_state = BaseState(Instruments(int(scene.fret_dance_instruments)))

        # 获取左手状态
        base_position = BasePositions(scene.fret_dance_base_positions)
        left_hand_state = LeftHandStates(scene.fret_dance_left_hand_states)

        # 获取右手状态
        right_hand_state = None
        for state in RightHandStates:
            if state.value == scene.fret_dance_right_hand_states:
                right_hand_state = state
                break

        if right_hand_state is None:
            self.report({'ERROR'}, "Invalid right hand state")
            return {'CANCELLED'}

        # 设置左手状态
        base_state.transfer_left_hand_state(
            base_position, left_hand_state, direction="set")

        # 设置右手状态
        base_state.transfer_right_hand_state(right_hand_state, direction="set")

        self.report({'INFO'}, "States have been set")
        return {'FINISHED'}


class FRET_DANCE_OT_load_state(Operator):
    """Load hand states from recorders to controllers"""
    bl_idname = "fret_dance.load_state"
    bl_label = "Load"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        base_state = BaseState(Instruments(int(scene.fret_dance_instruments)))

        # 获取左手状态
        base_position = BasePositions(scene.fret_dance_base_positions)
        left_hand_state = LeftHandStates(scene.fret_dance_left_hand_states)

        # 获取右手状态
        right_hand_state = None
        for state in RightHandStates:
            if state.value == scene.fret_dance_right_hand_states:
                right_hand_state = state
                break

        if right_hand_state is None:
            self.report({'ERROR'}, "Invalid right hand state")
            return {'CANCELLED'}

        # 加载左手状态
        base_state.transfer_left_hand_state(
            base_position, left_hand_state, direction="load")

        # 加载右手状态
        base_state.transfer_right_hand_state(
            right_hand_state, direction="load")

        self.report({'INFO'}, "States have been loaded")
        return {'FINISHED'}


class FRET_DANCE_OT_export_info(Operator, ExportHelper):
    """Export controller information to JSON file"""
    bl_idname = "fret_dance.export_info"
    bl_label = "Export Controller Info"
    bl_options = {'REGISTER', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ".json"

    __annotations__ = {
        "filter_glob": StringProperty(
            default="*.json",
            options={'HIDDEN'},
            maxlen=255,
        )
    }

    def execute(self, context):
        scene = context.scene
        base_state = BaseState(Instruments(int(scene.fret_dance_instruments)))

        # 导出控制器信息
        base_state.export_controller_info(self.filepath)

        self.report({'INFO'}, f"Controller info exported to {self.filepath}")
        return {'FINISHED'}


class FRET_DANCE_OT_import_info(Operator, ImportHelper):
    """Import controller information from JSON file"""
    bl_idname = "fret_dance.import_info"
    bl_label = "Import Controller Info"
    bl_options = {'REGISTER', 'UNDO'}

    # ExportHelper mixin class uses this
    filename_ext = ".json"

    __annotations__ = {
        "filter_glob": StringProperty(
            default="*.json",
            options={'HIDDEN'},
            maxlen=255,
        )
    }

    def execute(self, context):
        scene = context.scene
        base_state = BaseState(Instruments(int(scene.fret_dance_instruments)))

        try:
            # 导入控制器信息
            base_state.import_controller_info(self.filepath)
        except:
            self.report({'ERROR'}, "Import Controller Info Error")
            return {'CANCELLED'}

        self.report({'INFO'}, f"Controller info imported from {self.filepath}")
        return {'FINISHED'}


class FRET_DANCE_OT_select_animation_file(Operator, ImportHelper):
    """Select animation configuration file"""
    bl_idname = "fret_dance.select_animation_file"
    bl_label = "Select Animation Config"
    bl_options = {'REGISTER', 'UNDO'}

    # ImportHelper mixin class uses this
    filename_ext = ".json"

    __annotations__ = {
        "filter_glob": StringProperty(
            default="*.json",
            options={'HIDDEN'},
            maxlen=255,
        )
    }

    def execute(self, context):

        # 验证JSON文件结构
        try:
            with open(self.filepath, 'r') as f:
                data = json.load(f)

            # 检查必需的键是否存在
            required_keys = [
                "guitar_string_recorder_file",
                "left_hand_animation_file",
                "right_hand_animation_file"
            ]

            missing_keys = []
            for key in required_keys:
                if key not in data:
                    missing_keys.append(key)

            if missing_keys:
                self.report(
                    {'ERROR'}, f"Missing keys in JSON file: {', '.join(missing_keys)}")
                return {'CANCELLED'}

            # 检查文件路径是否存在
            missing_files = []
            for key in required_keys:
                file_path = data[key]
                if not os.path.exists(file_path):
                    missing_files.append(file_path)

            if missing_files:
                self.report(
                    {'WARNING'}, f"Following files not found: {', '.join(missing_files)}")

            self.report({'INFO'}, "Animation config file loaded successfully")
            # 设置选中的文件路径
            context.scene.fret_dance_animation_file = self.filepath
            return {'FINISHED'}

        except json.JSONDecodeError as e:
            self.report({'ERROR'}, f"Invalid JSON format: {str(e)}")
            return {'CANCELLED'}
        except Exception as e:
            self.report({'ERROR'}, f"Error reading file: {str(e)}")
            return {'CANCELLED'}


class FRET_DANCE_OT_generate_left_hand_animation(Operator):
    """Generate left hand animation from selected config file"""
    bl_idname = "fret_dance.generate_left_hand_animation"
    bl_label = "Generate Left Hand Animation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        config_path = scene.fret_dance_animation_file

        # 检查是否选择了配置文件
        if not config_path or not os.path.exists(config_path):
            self.report(
                {'ERROR'}, "Please select a valid animation configuration file")
            return {'CANCELLED'}

        try:
            # 读取配置文件
            with open(config_path, 'r') as f:
                config = json.load(f)

            # 清除左手现有关键帧
            clear_all_keyframe("Left_Hand_Controllers")

            # 应用左手动画数据
            if 'left_hand_animation_file' in config and os.path.exists(config['left_hand_animation_file']):
                animate_hand(config['left_hand_animation_file'])
                self.report(
                    {'INFO'}, "Left hand animation generation completed")
            else:
                self.report(
                    {'WARNING'}, "Left hand animation file not found or specified")
                return {'CANCELLED'}

            return {'FINISHED'}

        except Exception as e:
            self.report(
                {'ERROR'}, f"Failed to generate left hand animation: {str(e)}")
            return {'CANCELLED'}


class FRET_DANCE_OT_generate_right_hand_animation(Operator):
    """Generate right hand animation from selected config file"""
    bl_idname = "fret_dance.generate_right_hand_animation"
    bl_label = "Generate Right Hand Animation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        config_path = scene.fret_dance_animation_file

        # 检查是否选择了配置文件
        if not config_path or not os.path.exists(config_path):
            self.report(
                {'ERROR'}, "Please select a valid animation configuration file")
            return {'CANCELLED'}

        try:
            # 读取配置文件
            with open(config_path, 'r') as f:
                config = json.load(f)

            # 清除右手现有关键帧
            clear_all_keyframe("Right_Hand_Controllers")

            # 应用右手动画数据
            if 'right_hand_animation_file' in config and os.path.exists(config['right_hand_animation_file']):
                animate_hand(
                    config['right_hand_animation_file'])
                self.report(
                    {'INFO'}, "Right hand animation generation completed")
            else:
                self.report(
                    {'WARNING'}, "Right hand animation file not found or specified")
                return {'CANCELLED'}

            return {'FINISHED'}

        except Exception as e:
            self.report(
                {'ERROR'}, f"Failed to generate right hand animation: {str(e)}")
            return {'CANCELLED'}


class FRET_DANCE_OT_generate_string_animation(Operator):
    """Generate string animation from selected config file"""
    bl_idname = "fret_dance.generate_string_animation"
    bl_label = "Generate String Animation"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        config_path = scene.fret_dance_animation_file

        # 检查是否选择了配置文件
        if not config_path or not os.path.exists(config_path):
            self.report(
                {'ERROR'}, "Please select a valid animation configuration file")
            return {'CANCELLED'}

        try:
            # 读取配置文件
            with open(config_path, 'r') as f:
                config = json.load(f)

            clear_string_aniamtion()

            # 应用弦动画数据
            if 'guitar_string_recorder_file' in config and os.path.exists(config['guitar_string_recorder_file']):
                animate_string(
                    config['guitar_string_recorder_file'])
                self.report({'INFO'}, "String animation generation completed")
            else:
                self.report(
                    {'WARNING'}, "String animation file not found or specified")
                return {'CANCELLED'}

            return {'FINISHED'}

        except Exception as e:
            self.report(
                {'ERROR'}, f"Failed to generate string animation: {str(e)}")
            return {'CANCELLED'}


class FRET_DANCE_OT_generate_all_animation(Operator):
    """Generate all animations from selected config file"""
    bl_idname = "fret_dance.generate_all_animation"
    bl_label = "Generate All Animations"
    bl_options = {'REGISTER', 'UNDO'}

    def execute(self, context):
        scene = context.scene
        config_path = scene.fret_dance_animation_file

        # 检查是否选择了配置文件
        if not config_path or not os.path.exists(config_path):
            self.report(
                {'ERROR'}, "Please select a valid animation configuration file")
            return {'CANCELLED'}

        try:
            # 读取配置文件
            with open(config_path, 'r') as f:
                config = json.load(f)

            # 清除所有现有关键帧
            clear_all_keyframe("Left_Hand_Controllers")
            clear_all_keyframe("Right_Hand_Controllers")
            clear_string_aniamtion()

            # 应用所有动画数据
            success_count = 0

            if 'left_hand_animation_file' in config and os.path.exists(config['left_hand_animation_file']):
                animate_hand(config['left_hand_animation_file'])
                success_count += 1
            else:
                self.report(
                    {'WARNING'}, "Left hand animation file not found or specified")

            if 'right_hand_animation_file' in config and os.path.exists(config['right_hand_animation_file']):
                animate_hand(
                    config['right_hand_animation_file'])
                success_count += 1
            else:
                self.report(
                    {'WARNING'}, "Right hand animation file not found or specified")

            if 'guitar_string_recorder_file' in config and os.path.exists(config['guitar_string_recorder_file']):
                animate_string(
                    config['guitar_string_recorder_file'])
                success_count += 1
            else:
                self.report(
                    {'WARNING'}, "String animation file not found or specified")

            if success_count > 0:
                self.report({'INFO'}, "All animations generation completed")
                return {'FINISHED'}
            else:
                self.report({'ERROR'}, "No animation files found or specified")
                return {'CANCELLED'}

        except Exception as e:
            self.report({'ERROR'}, f"Failed to generate animations: {str(e)}")
            return {'CANCELLED'}


class FRET_DANCE_PT_main_panel(Panel):
    """Creates a Panel in the 3D View sidebar"""
    bl_label = "FretDance Controller Setup"
    bl_idname = "FRET_DANCE_PT_main_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = "FretDance"

    def draw(self, context):
        layout = self.layout
        scene = context.scene

        # 第一大块：INIT
        box = layout.box()
        box.label(text="初始化", icon='TOOL_SETTINGS')
        row = box.row()
        row.prop(scene, "fret_dance_instruments")
        row = box.row(align=True)
        row.operator("fret_dance.check_status")
        row.operator("fret_dance.setup_objects")
        row = box.row()
        row.operator("wm.mmd2blender_initialize", text="初始化mmd骨骼")

        # 第二大块：Choose left hand state
        box = layout.box()
        box.label(text="选择左手状态", icon='HAND')
        row = box.row()
        row.prop(scene, "fret_dance_base_positions")
        row = box.row()
        row.prop(scene, "fret_dance_left_hand_states")

        # 第三大块：Choose right hand state
        box = layout.box()
        box.label(text="选择右手状态", icon='RIGHTARROW_THIN')
        row = box.row()
        row.prop(scene, "fret_dance_right_hand_states")

        # 第四大块：Set and Load
        box = layout.box()
        box.label(text="设置与加载", icon='FILE_REFRESH')
        row = box.row(align=True)
        row.operator("fret_dance.set_state")
        row.operator("fret_dance.load_state")

        # 保存控制信息
        box = layout.box()
        box.label(text="导入/导出人物信息", icon='EXPORT')
        row = box.row(align=True)
        row.operator("fret_dance.import_info", text="导入")
        row.operator("fret_dance.export_info", text="导出")

        # 动画生成部分
        box = layout.box()
        box.label(text="生成动画", icon='PLAY')
        row = box.row()
        row.prop(scene, "fret_dance_animation_file", text="")
        row = box.row()
        row.operator("fret_dance.select_animation_file", text="选择动画文件")

        row = box.row(align=True)
        row.operator("fret_dance.generate_left_hand_animation",
                     text="左手动画")
        row.operator("fret_dance.generate_right_hand_animation",
                     text="右手动画")

        row = box.row(align=True)
        row.operator("fret_dance.generate_string_animation", text="弦动画")
        row = box.row()
        row.operator("fret_dance.generate_all_animation", text="一键生成全部动画")


def register():
    # 注册枚举属性
    bpy.types.Scene.fret_dance_instruments = EnumProperty(
        name="Instrument",
        description="Select instrument type",
        items=[
            ('0', "Finger Style Guitar", "Finger style guitar"),
            ('1', "Electric Guitar", "Electric guitar"),
            ('2', "Bass", "Bass guitar"),
        ],
        default='0'
    )

    bpy.types.Scene.fret_dance_base_positions = EnumProperty(
        name="Position",
        description="Select base position",
        items=[
            ('P0', "P0", "Position 0"),
            ('P1', "P1", "Position 1"),
            ('P2', "P2", "Position 2"),
            ('P3', "P3", "Position 3"),
        ],
        default='P0'
    )

    bpy.types.Scene.fret_dance_left_hand_states = EnumProperty(
        name="State",
        description="Select left hand state",
        items=[
            ('Normal', "Normal", "Normal state"),
            ('Outer', "Outer", "Outer state"),
            ('Inner', "Inner", "Inner state"),
            ('Barre', "Barre", "Barre state"),
        ],
        default='Normal'
    )

    bpy.types.Scene.fret_dance_right_hand_states = EnumProperty(
        name="State",
        description="Select right hand state",
        items=[
            ('0', "Low", "Low position"),
            ('end', "End", "End position"),
            ('3', "High", "High position"),
        ],
        default='0'
    )

    bpy.types.Scene.fret_dance_animation_file = StringProperty(
        name="Animation Config File",
        description="Path to animation configuration JSON file",
        subtype='FILE_PATH'
    )

    # 注册类
    bpy.utils.register_class(FRET_DANCE_OT_setup_objects)
    bpy.utils.register_class(FRET_DANCE_OT_check_status)
    bpy.utils.register_class(FRET_DANCE_OT_set_state)
    bpy.utils.register_class(FRET_DANCE_OT_load_state)
    bpy.utils.register_class(FRET_DANCE_OT_export_info)
    bpy.utils.register_class(FRET_DANCE_OT_import_info)
    bpy.utils.register_class(WM_OT_mmd2blender_initialize)
    bpy.utils.register_class(FRET_DANCE_PT_main_panel)
    bpy.utils.register_class(FRET_DANCE_OT_select_animation_file)
    bpy.utils.register_class(FRET_DANCE_OT_generate_left_hand_animation)
    bpy.utils.register_class(FRET_DANCE_OT_generate_right_hand_animation)
    bpy.utils.register_class(FRET_DANCE_OT_generate_string_animation)
    bpy.utils.register_class(FRET_DANCE_OT_generate_all_animation)


def unregister():
    # 注销类
    bpy.utils.unregister_class(FRET_DANCE_PT_main_panel)
    bpy.utils.unregister_class(FRET_DANCE_OT_export_info)
    bpy.utils.unregister_class(FRET_DANCE_OT_import_info)
    bpy.utils.unregister_class(FRET_DANCE_OT_load_state)
    bpy.utils.unregister_class(FRET_DANCE_OT_set_state)
    bpy.utils.unregister_class(FRET_DANCE_OT_check_status)
    bpy.utils.unregister_class(FRET_DANCE_OT_setup_objects)
    bpy.utils.unregister_class(WM_OT_mmd2blender_initialize)
    bpy.utils.unregister_class(FRET_DANCE_OT_select_animation_file)
    bpy.utils.unregister_class(FRET_DANCE_OT_generate_all_animation)
    bpy.utils.unregister_class(FRET_DANCE_OT_generate_string_animation)
    bpy.utils.unregister_class(FRET_DANCE_OT_generate_right_hand_animation)
    bpy.utils.unregister_class(FRET_DANCE_OT_generate_left_hand_animation)

    # 删除属性
    del bpy.types.Scene.fret_dance_instruments
    del bpy.types.Scene.fret_dance_base_positions
    del bpy.types.Scene.fret_dance_left_hand_states
    del bpy.types.Scene.fret_dance_right_hand_states
    del bpy.types.Scene.fret_dance_animation_file


if __name__ == "__main__":
    register()
