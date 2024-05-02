import bpy
import json
import mathutils

# 从外部读取json文件
avatar = 'rem'
midi_name = "Corridors Of Time Fingerstyle"

left_hand_animation = f"G:/fretDance/output/{avatar}_{midi_name}_lefthand_animation.json"
right_hand_animation = f"G:/fretDance/output/{avatar}_{midi_name}_righthand_animation.json"

def animate_hand(animation_file: str):    

    # 读取json文件
    with open(animation_file, "r") as f:
        handDicts = json.load(f)

        # 将所有的帧存储在一个列表中
        frames = [int(hand["frame"]) for hand in handDicts]

        for i in range(len(frames)):
            frame = frames[i]
            fingerInfos = handDicts[i]["fingerInfos"]

            # 将blender时间帧设置到frame
            bpy.context.scene.frame_set(frame)
            insert_values(fingerInfos)

            # 如果当前帧和下一帧的差值大于3，则在两帧之间插入额外的帧
            if i < len(frames) - 1 and frames[i + 1] - frame > 3:
                for extra_frame in range(frame + 1, frames[i + 1]):
                    bpy.context.scene.frame_set(extra_frame)
                    insert_values(fingerInfos)


def insert_values(fingerInfos):
    # 设置每个controller的值
    for fingerInfo in fingerInfos:
        try:
            obj = bpy.data.objects[fingerInfo]
            value = fingerInfos[fingerInfo]
            if "rotation" in fingerInfo:
                obj.rotation_euler = value
                obj.keyframe_insert(data_path="rotation_euler")
            else:
                # 把value从base_bone的坐标系转换到世界坐标系
                value = mathutils.Vector(value)
                obj.location = value
                obj.keyframe_insert(data_path="location")
        except:
            pass


animate_hand(left_hand_animation)
animate_hand(right_hand_animation)
