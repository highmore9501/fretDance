import bpy

# 第一步，选移动所有模型到Collection


def clear_collections():
    daz_collection = 'DAZ_FIG_0'

    # 获取源 collection 和目标 collection
    source_collection = bpy.data.collections.get(daz_collection)
    target_collection = bpy.data.collections.get("Collection")

    # 检查源 collection 和目标 collection 是否存在
    if source_collection and target_collection:
        # 遍历源 collection 中的所有对象
        for obj in source_collection.objects:
            # 从源 collection 中移除对象
            source_collection.objects.unlink(obj)

            # 将对象添加到目标 collection 中
            target_collection.objects.link(obj)

# 第二步，删除除了collection以外的所有其它collection和它们下面的内容


def remove_all_collections_except_collection():
    daz_collection = bpy.data.collections.get('Collection')
    if daz_collection:
        for coll in bpy.data.collections:
            if coll != daz_collection:
                bpy.data.collections.remove(coll)


# 第三步，去掉所有的自定义骨骼形状，去掉所有的ik_limit，去掉所有的约束器
def modify_daz_studio_bones(armature_name):
    """
    usage: 将骨骼的自定义形状去掉
    """
    armature = bpy.data.objects[armature_name]
    # 选中armature
    bpy.ops.object.mode_set(mode='OBJECT')
    selected_bones = armature.data.edit_bones

    # 切换到编辑模式
    bpy.ops.object.mode_set(mode='EDIT')
    for bone in selected_bones:
        if bone.name.startswith('l'):
            bone.name = bone.name[1:] + "_L"
        elif bone.name.startswith('r'):
            bone.name = bone.name[1:] + "_R"

    # 切换回pose模式
    bpy.ops.object.mode_set(mode='POSE')
    # 选中全部pose_bone
    selected_bones = armature.pose.bones

    for bone in selected_bones:
        if bone.custom_shape:
            bone.custom_shape = None
        bone.use_ik_limit_x = False
        bone.use_ik_limit_y = False
        bone.use_ik_limit_z = False
        bone.lock_ik_x = False
        bone.lock_ik_y = False
        bone.lock_ik_z = False
        for constraint in bone.constraints:
            bone.constraints.remove(constraint)

# 第四步，创建face_Bone_collection，把脸部骨骼全移进去


def create_face_bone_collections():
    armature = bpy.data.armatures[0]
    face_collection = armature.collections.new("Face")

    def find_bone_in_hierarchy(bone, target_bone_name):
        if bone.name == target_bone_name:
            return True
        if bone.parent:
            return find_bone_in_hierarchy(bone.parent, target_bone_name)
        return False

    # 遍历armature上所有骨骼，如果骨骼的parent往上回溯到head，则将这个骨骼添加到face_collection中
    for bone in armature.bones:
        if find_bone_in_hierarchy(bone, "head"):
            face_collection.assign(bone)

# 第五步，生成手臂的MCH骨骼


def creat_arm_MCH_bones(armature_name):
    armature = bpy.data.armatures[0]
    # 选中armature以后进入编辑模式
    bpy.ops.object.mode_set(mode='EDIT')

    def creat_arm_MCH_bone_v3(first_bone_name: str, second_bone_name_str, MCH_bone_name: str):
        # 生成一根新MCH骨骼
        new_bone = armature.edit_bones.new(MCH_bone_name)
        # 将MCH骨骼的头部设置成first_bone的头部
        new_bone.head = armature.edit_bones[first_bone_name].head
        # 将MCH骨骼的尾部设置成second_bone的尾部
        new_bone.tail = armature.edit_bones[second_bone_name_str].tail
        # 将MCH骨骼的roll设置成first_bone的roll
        new_bone.roll = armature.edit_bones[first_bone_name].roll
        # 将MCH骨骼的parent设置成first_bone的parent
        new_bone.parent = armature.edit_bones[first_bone_name].parent
        # 将deform设置为false
        new_bone.use_deform = False

        # 将第一块和第二块骨骼的parent都设置成mch_bone
        armature.edit_bones[first_bone_name].parent = new_bone
        armature.edit_bones[second_bone_name_str].parent = new_bone

        # 将第一块骨骼的尾部设置成第二块骨骼的头部
        armature.edit_bones[first_bone_name].tail = armature.edit_bones[second_bone_name_str].head

    def creat_arm_MCH_bone_v2(original_bone_name: str):
        MCH_bone_name = "MCH_" + original_bone_name
        original_bone = armature.edit_bones[original_bone_name]
        new_bone = armature.edit_bones.new(MCH_bone_name)
        new_bone.head = original_bone.head
        new_bone.tail = original_bone.tail
        new_bone.roll = original_bone.roll
        new_bone.parent = original_bone.parent
        new_bone.use_deform = False
        original_bone.parent = new_bone

    if armature_name == 'Genesis3Female':
        task_list = [{
            "first_bone_name": "ShldrBend",
            "second_bone_name_str": "ShldrTwist",
            "MCH_bone_name": "MCH_arm"
        }, {
            "first_bone_name": "ForearmBend",
            "second_bone_name_str": "ForearmTwist",
            "MCH_bone_name": "MCH_forearm"
        }]

        suffix = ['_L', '_R']

        for task in task_list:
            for post in suffix:
                creat_arm_MCH_bone_v3(task["first_bone_name"] + post,
                                      task["second_bone_name_str"] + post, task["MCH_bone_name"] + post)
        # 把mch_forearm的parent设置成mch_arm并且把头设置成mch_arm的尾部
        armature.edit_bones["MCH_forearm_L"].parent = armature.edit_bones["MCH_arm_L"]
        armature.edit_bones["MCH_forearm_L"].head = armature.edit_bones["MCH_arm_L"].tail
        armature.edit_bones["MCH_forearm_R"].parent = armature.edit_bones["MCH_arm_R"]
        armature.edit_bones["MCH_forearm_R"].head = armature.edit_bones["MCH_arm_R"].tail
    elif armature_name == 'Genesis2Female':
        task_list = ['Shldr', 'ForeArm']
        suffix = ['_L', '_R']

        for task in task_list:
            for post in suffix:
                creat_arm_MCH_bone_v2(task + post)

# 第六步，生成手指的mch骨骼


def creat_finger_MCH_bones():
    armature = bpy.data.armatures[0]
    # 选中armature以后进入编辑模式
    bpy.ops.object.mode_set(mode='EDIT')

    def creat_finger_MCH_bone(finger_name: str, suffix: str):
        three_finger_name = [finger_name +
                             str(i) + suffix for i in range(1, 4)]

        for sub_finger_name in three_finger_name:
            current_finger = armature.edit_bones[sub_finger_name]
            mch_name = "MCH_" + sub_finger_name
            new_bone = armature.edit_bones.new(mch_name)
            new_bone.head = current_finger.head
            new_bone.tail = current_finger.tail
            new_bone.roll = current_finger.roll
            new_bone.parent = current_finger.parent
            new_bone.use_deform = False
            current_finger.parent = new_bone

        for i in range(2, 4):
            current_mch_bone = armature.edit_bones[f"MCH_{finger_name}{i}{suffix}"]
            current_mch_bone.head = armature.edit_bones[f"MCH_{finger_name}{i-1}{suffix}"].tail
            current_mch_bone.parent = armature.edit_bones[f"MCH_{finger_name}{i-1}{suffix}"]

    fingers = ['Thumb', 'Index', 'Mid', 'Ring', 'Pinky']
    suffixs = ['_L', '_R']

    for finger in fingers:
        for suffix in suffixs:
            creat_finger_MCH_bone(finger, suffix)

# 第七步，生成手腕的mch骨骼


def creat_wrist_MCH_bones(armature_name):
    armature = bpy.data.armatures[0]
    # 进入编辑模式
    bpy.ops.object.mode_set(mode='EDIT')

    def creat_wrist_MCH_bone(wrist_name: str, suffix: str, armature_name: str):
        wrist_bone = armature.edit_bones[wrist_name + suffix]
        mch_name = "MCH_" + wrist_name + suffix
        new_bone = armature.edit_bones.new(mch_name)
        new_bone.head = wrist_bone.head
        new_bone.tail = wrist_bone.tail
        new_bone.roll = wrist_bone.roll
        forearm_name_prefix = "MCH_forearm" if armature_name == "Genesis3Female" else "MCH_ForeArm"
        forearm_name = forearm_name_prefix + suffix
        new_bone.parent = armature.edit_bones[forearm_name]
        new_bone.use_deform = False
        wrist_bone.parent = new_bone

    suffixs = ['_L', '_R']
    wrist_name = 'Hand'
    for suffix in suffixs:
        creat_wrist_MCH_bone(wrist_name, suffix, armature_name)


# 从这里开始的步骤要先从其它文件导入controller以后才能执行
def change_hand_bone_rotation():
    armature = bpy.data.armatures[0]
    # 选中armature以后进入POSE模式
    bpy.ops.object.mode_set(mode='POSE')

    suffixs = ['_L', '_R']
    wrist_name = 'Hand'
    for suffix in suffixs:
        wrist_bone = bpy.context.active_object.pose.bones[wrist_name+suffix]
        wrist_bone.rotation_mode = 'ZXY'


def add_constraints(armature_name):
    armature = bpy.data.armatures[0]
    # 选中armature以后进入POSE模式
    bpy.ops.object.mode_set(mode='POSE')

    def add_IK(bone_name: str, targetA_name: str, suffix: str, targetB_name: str = None, chain_count: int = 2):
        bone = bpy.context.active_object.pose.bones[bone_name + suffix]
        constraint = bone.constraints.new(type='IK')
        targetA = bpy.data.objects[targetA_name+suffix]
        constraint.target = targetA
        if targetB_name is not None:
            targetB = bpy.data.objects[targetB_name+suffix]
            constraint.pole_target = targetB
        constraint.chain_count = chain_count

    IK_tasks = [
        {
            'bone_name': 'MCH_forearm' if armature_name == 'Genesis3Female' else 'MCH_ForeArm',
            'targetA_name': 'H',
            'targetB_name': 'HP',
            'chain_count': 2
        },
        {
            'bone_name': 'MCH_Thumb3',
            'targetA_name': 'T',
            'targetB_name': 'TP',
            'chain_count': 3
        },
        {
            'bone_name': 'MCH_Index3',
            'targetA_name': 'I',
            'targetB_name': None,
            'chain_count': 3
        },
        {
            'bone_name': 'MCH_Mid3',
            'targetA_name': 'M',
            'targetB_name': None,
            'chain_count': 3
        },
        {
            'bone_name': 'MCH_Ring3',
            'targetA_name': 'R',
            'targetB_name': None,
            'chain_count': 3
        },
        {
            'bone_name': 'MCH_Pinky3',
            'targetA_name': 'P',
            'targetB_name': None,
            'chain_count': 3
        },
    ]
    suffixs = ['_L', '_R']

    for task in IK_tasks:
        for suffix in suffixs:
            add_IK(task['bone_name'], task['targetA_name'], suffix,
                   task['targetB_name'], task['chain_count'])

    def add_copy_rotation(bone_name: str, target_name: str, suffix: str, isY: bool, influence: float):
        bone = bpy.context.active_object.pose.bones[bone_name + suffix]
        constraint = bone.constraints.new(type='COPY_ROTATION')
        target = bpy.data.objects[target_name+suffix]
        constraint.target = target
        constraint.target_space = 'WORLD'
        constraint.owner_space = 'LOCAL'
        if isY:
            constraint.use_z = False
            constraint.use_x = False
        else:
            constraint.use_y = False
        constraint.influence = influence

    target_name = 'H_rotation'
    rotation_tasks = [
        {
            'bone_name': 'Hand',
            'isY': True,
            'influence': 1
        },
        {
            'bone_name': 'MCH_Hand',
            'isY': False,
            'influence': 1
        },
        {
            'bone_name': 'ForearmTwist',
            'isY': True,
            'influence': 0.9
        },
        {
            'bone_name': 'ForearmBend',
            'isY': True,
            'influence': 0.7
        },
        {
            'bone_name': 'ShldrTwist',
            'isY': True,
            'influence': 0.5
        },
        {
            'bone_name': 'ShldrBend',
            'isY': True,
            'influence': 0.3
        }
    ]

    for task in rotation_tasks:
        for suffix in suffixs:
            try:
                add_copy_rotation(task['bone_name'], target_name, suffix,
                                  task['isY'], task['influence'])
            except:
                print(task['bone_name'], target_name, suffix)


def add_locked_tracks(armature_name):
    armature = bpy.data.armatures[0]
    # 选中armature以后进入edit模式
    bpy.ops.object.mode_set(mode='EDIT')

    def add_locked_track_targets(bone_name: str, suffix: str):
        source_bone = armature.edit_bones[bone_name + suffix]
        # 计算source_bone的头尾方向
        direction = source_bone.tail - source_bone.head
        # normalize direction
        direction = direction / direction.length
        copyed_bone = armature.edit_bones.new('MCH_'+bone_name+suffix)
        # copyed_bone朝direction方向移动30cm，然后往z轴方向向下移动30cm
        copyed_bone.head = source_bone.head + direction * 0.3
        copyed_bone.head[2] -= 0.3
        copyed_bone.tail = source_bone.tail + direction * 0.3
        copyed_bone.tail[2] -= 0.3
        copyed_bone.parent = source_bone.parent
        copyed_bone.roll = source_bone.roll
        copyed_bone.use_deform = False

    target_name = 'Carpal'
    suffixs = ['_L', '_R']

    carpal_num = 5 if armature_name == 'Genesis3Female' else 3

    for i in range(1, carpal_num):
        for suffix in suffixs:
            add_locked_track_targets(target_name+str(i), suffix)

    # 切换到pose模式
    bpy.ops.object.mode_set(mode='POSE')

    def add_locked_track(bone_name: str, target_name: str, suffix: str, influence: float):
        bone = bpy.context.active_object.pose.bones[bone_name + suffix]
        constraint = bone.constraints.new(type='LOCKED_TRACK')
        target_full_name = 'MCH_'+target_name+suffix
        constraint.target = bpy.data.objects[armature_name]
        constraint.subtarget = target_full_name
        constraint.track_axis = 'TRACK_Z'
        constraint.lock_axis = 'LOCK_Y'
        constraint.influence = influence

    add_locked_track_tasks = [
        {
            'bone_name': 'Index3',
            'target_name': 'Carpal1',
            'influence': 0.8
        },
        {
            'bone_name': 'Index2',
            'target_name': 'Carpal1',
            'influence': 0.3
        },
        {
            'bone_name': 'Mid3',
            'target_name': 'Carpal2' if armature_name == 'Genesis3Female' else 'Carpal1',
            'influence': 0.8
        },
        {
            'bone_name': 'Mid2',
            'target_name': 'Carpal2' if armature_name == 'Genesis3Female' else 'Carpal1',
            'influence': 0.3
        },
        {
            'bone_name': 'Ring3',
            'target_name': 'Carpal3' if armature_name == 'Genesis3Female' else 'Carpal2',
            'influence': 0.8
        },
        {
            'bone_name': 'Ring2',
            'target_name': 'Carpal3' if armature_name == 'Genesis3Female' else 'Carpal2',
            'influence': 0.3
        },
        {
            'bone_name': 'Pinky3',
            'target_name': 'Carpal4' if armature_name == 'Genesis3Female' else 'Carpal2',
            'influence': 0.8
        },
        {
            'bone_name': 'Pinky2',
            'target_name': 'Carpal4' if armature_name == 'Genesis3Female' else 'Carpal2',
            'influence': 0.3
        }
    ]

    for task in add_locked_track_tasks:
        for suffix in suffixs:
            try:
                add_locked_track(task['bone_name'], task['target_name'], suffix,
                                 task['influence'])
            except:
                print(task['bone_name'], task['target_name'], suffix)


def move_MCH_bones():
    armature = bpy.data.armatures[0]
    mch_collection = armature.collections.new("MCH")

    for bone in armature.bones:
        if bone.name.startswith("MCH_"):
            mch_collection.assign(bone)


# 导入控制器之前的操作


def before_controller_export(armature_name):
    clear_collections()
    remove_all_collections_except_collection()
    modify_daz_studio_bones(armature_name)
    create_face_bone_collections()
    creat_arm_MCH_bones(armature_name)
    creat_finger_MCH_bones()
    creat_wrist_MCH_bones(armature_name)

# 导入控制器之后的操作


def after_controller_export(armature_name):
    change_hand_bone_rotation()
    add_constraints(armature_name)
    add_locked_tracks(armature_name)
    move_MCH_bones()
