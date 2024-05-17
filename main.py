import gradio as gr
import os

from FretDaner import main
from src.midi.midiToNote import export_midi_info

# 设定各弦音高的选项
defalut_guitar_string_notes_options = ["e", "b", "G", "D", "A", "E1"]

# 所有可能是弦音高的note
all_notes = [
    "C2", "C#2", "D2", "D#2", "E2", "F2", "F#2", "G2", "G#2", "A2", "A#2", "B2",
    "C1", "C#1", "D1", "D#1", "E1", "F1", "F#1", "G1", "G#1", "A1", "A#1", "B1",
    "C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B",
    "c", "c#", "d", "d#", "e", "f", "f#", "g", "g#", "a", "a#", "b",
]

# 添加吉他类型的选项
guitar_type_options = {
    "guitar": "e, b, G, D, A, E1",
    "bass": "G1, D1, A2, E2"
}


def check_and_exec(avatar, midiFilePath, track_number, channel_number, FPS, guitar_type, use_custom_string_notes, custom_string_notes) -> str:
    # 根据复选框的值决定使用哪个弦音高
    if use_custom_string_notes:
        guitar_string_notes = custom_string_notes.replace(' ', '').split(',')
    else:
        guitar_string_notes = guitar_type_options[guitar_type].replace(
            ' ', '').split(',')
    # 检查列表中的每个元素是否在all_notes中
    for note in guitar_string_notes:
        if note not in all_notes:
            return "Invalid note: " + note

    midi_path = "asset/midi/" + midiFilePath
    result = main(avatar, midi_path, track_number,
                  channel_number, FPS, guitar_string_notes)
    return result


# 获取指定路径下的所有 JSON 和 MIDI 文件
def refresh_asset_files():
    global json_files, midi_files
    json_files = [f.split(".")[0] for f in os.listdir(
        "asset/controller_infos") if f.endswith(".json")]
    midi_files = [f for f in os.listdir("asset/midi") if f.endswith(".mid")]


refresh_asset_files()

with gr.Blocks() as demo:
    with gr.Row() as avatar_selection_container:
        with gr.Column():
            refresh_button = gr.Button("Refresh asset 刷新asset文件夹信息")
            refresh_button.click(fn=refresh_asset_files)
            midi_dropdown = gr.Dropdown(
                midi_files, label="select midi 选择在目录asset/midi下面的MIDI 文件")
            submit_check_midi_button = gr.Button(
                "scan midi info扫描 MIDI 文件信息")
            midi_info_text = gr.Textbox(label="MIDI 文件信息")
            submit_check_midi_button.click(fn=export_midi_info, inputs=[
                midi_dropdown], outputs=midi_info_text)

        with gr.Column() as avatar_container:
            track_number = gr.Number(
                minimum=0, maximum=100, value=0, step=1, label="select track 选择 MIDI 文件的音轨编号")
            channel_number = gr.Number(
                minimum=-1, maximum=100, value=-1, step=1, label="select channel 选择 MIDI 文件的通道编号，如果为-1表示接受所有通道")
            fps_number = gr.Number(
                minimum=1, maximum=120, value=30, step=1, label="set fps 设定 Blender 里的 FPS")

        # 创建一个新的容器
        with gr.Column() as custom_string_notes_container:
            avatar_dropdown = gr.Dropdown(
                json_files, label="select player 选择角色，后缀为_E的角色是使用的电吉它，要确保midi文件也是电吉他的谱子")
            # 添加吉他类型的下拉菜单
            guitar_type_dropdown = gr.Dropdown(
                guitar_type_options.keys(), label="select guitar type 选择吉他类型")
            # 将复选框和文本框添加到容器中
            use_custom_string_notes_checkbox = gr.Checkbox(
                label="use custom string notes 是否使用自定义弦音高。勾选这个以后，吉它类型的选择将变为无效")
            custom_string_notes_textbox = gr.Textbox(
                value="e, b, G, D, A, E1", label="custom string notes 可以自定义弦数量和音高，用逗号分隔，以下是标准吉它的定弦示范")

    with gr.Row() as output_container:
        submit_button = gr.Button(value="submit 提交")
        output_textbox = gr.Textbox(label="输出结果")

        submit_button.click(check_and_exec, inputs=[
            avatar_dropdown, midi_dropdown, track_number, channel_number, fps_number, guitar_type_dropdown, use_custom_string_notes_checkbox, custom_string_notes_textbox], outputs=[output_textbox])


demo.launch(inbrowser=True)
