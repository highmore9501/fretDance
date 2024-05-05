import gradio as gr
import os

from FretDaner import main

# 设定各弦音高的选项
defalut_guitar_string_notes_options = ["e", "b", "G", "D", "A", "E1"]

# 所有可能是弦音高的note
all_notes = [
    "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2",
    "C1", "C#1", "D1", "D#1", "E1", "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1",
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
    "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b",
]

# 获取指定路径下的所有 JSON 和 MIDI 文件
json_files = [f.split(".")[0] for f in os.listdir(
    "asset/controller_infos") if f.endswith(".json")]
midi_files = ["asset/midi/" + f for f in os.listdir(
    "asset/midi") if f.endswith(".mid")]


def check_and_exec(avatar, midiFilePath, FPS, guitar_string_notes) -> str:
    # 将逗号分隔的字符串转换为列表
    guitar_string_notes = guitar_string_notes.replace(' ', '').split(',')
    # 检查列表中的每个元素是否在all_notes中
    for note in guitar_string_notes:
        if note not in all_notes:
            return "Invalid note: " + note
    result = main(avatar, midiFilePath, FPS, guitar_string_notes)
    return result


with gr.Blocks() as demo:
    avatar_dropdown = gr.Dropdown(json_files, label="选择角色")
    midi_dropdown = gr.Dropdown(midi_files, label="选择在目录asset/midi下面的MIDI 文件")
    fps_number = gr.Number(
        minimum=1, maximum=120, value=30, step=1, label="设定 Blender 里的 FPS")
    guitar_string_notes_textbox = gr.Textbox(
        value="e, b, G, D, A, E1", label="输入吉他弦音高，用逗号分隔")
    output_textbox = gr.Textbox(label="输出结果")
    submit_button = gr.Button(value="提交")
    submit_button.click(check_and_exec, inputs=[
                        avatar_dropdown, midi_dropdown, fps_number, guitar_string_notes_textbox], outputs=[output_textbox])

demo.launch(inbrowser=True)
