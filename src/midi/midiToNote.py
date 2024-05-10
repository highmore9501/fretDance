from mido import MidiFile
from typing import List
import random

MIDI_INSTRUMENTS = [
    "Acoustic Grand Piano", "Bright Acoustic Piano", "Electric Grand Piano", "Honky-tonk Piano", "Electric Piano 1", "Electric Piano 2", "Harpsichord", "Clavi",
    "Celesta", "Glockenspiel", "Music Box", "Vibraphone", "Marimba", "Xylophone", "Tubular Bells", "Dulcimer",
    "Drawbar Organ", "Percussive Organ", "Rock Organ", "Church Organ", "Reed Organ", "Accordion", "Harmonica", "Tango Accordion",
    "Acoustic Guitar (nylon)", "Acoustic Guitar (steel)", "Electric Guitar (jazz)", "Electric Guitar (clean)", "Electric Guitar (muted)", "Overdriven Guitar", "Distortion Guitar", "Guitar Harmonics",
    "Acoustic Bass", "Electric Bass (finger)", "Electric Bass (pick)", "Fretless Bass", "Slap Bass 1", "Slap Bass 2", "Synth Bass 1", "Synth Bass 2",
    "Violin", "Viola", "Cello", "Contrabass", "Tremolo Strings", "Pizzicato Strings", "Orchestral Harp", "Timpani",
    "String Ensemble 1", "String Ensemble 2", "Synth Strings 1", "Synth Strings 2", "Choir Aahs", "Voice Oohs", "Synth Voice", "Orchestra Hit",
    "Trumpet", "Trombone", "Tuba", "Muted Trumpet", "French Horn", "Brass Section", "Synth Brass 1", "Synth Brass 2",
    "Soprano Sax", "Alto Sax", "Tenor Sax", "Baritone Sax", "Oboe", "English Horn", "Bassoon", "Clarinet",
    "Piccolo", "Flute", "Recorder", "Pan Flute", "Blown Bottle", "Shakuhachi", "Whistle", "Ocarina",
    "Lead 1 (square)", "Lead 2 (sawtooth)", "Lead 3 (calliope)", "Lead 4 (chiff)", "Lead 5 (charang)", "Lead 6 (voice)", "Lead 7 (fifths)", "Lead 8 (bass + lead)",
    "Pad 1 (new age)", "Pad 2 (warm)", "Pad 3 (polysynth)", "Pad 4 (choir)", "Pad 5 (bowed)", "Pad 6 (metallic)", "Pad 7 (halo)", "Pad 8 (sweep)",
    "FX 1 (rain)", "FX 2 (soundtrack)", "FX 3 (crystal)", "FX 4 (atmosphere)", "FX 5 (brightness)", "FX 6 (goblins)", "FX 7 (echoes)", "FX 8 (sci-fi)",
    "Sitar", "Banjo", "Shamisen", "Koto", "Kalimba", "Bagpipe", "Fiddle", "Shanai",
    "Tinkle Bell", "Agogo", "Steel Drums", "Woodblock", "Taiko Drum", "Melodic Tom", "Synth Drum", "Reverse Cymbal",
    "Guitar Fret Noise", "Breath Noise", "Seashore", "Bird Tweet", "Telephone Ring", "Helicopter", "Applause", "Gunshot"
]


def calculate_frame(tempo_changes, ticks_per_beat, FPS, real_tick) -> int:
    total_frames = 0
    for i in range(len(tempo_changes)):
        current_track, current_tempo, current_time = tempo_changes[i]

        # 如果当前的时间已经超过了real_tick，那么就停止计算
        if current_time > real_tick:
            break

        # 获取下一个时间点，如果没有下一个时间点，或者下一个时间点超过了real_tick，那么就使用real_tick
        next_time = min(tempo_changes[i + 1][2] if i + 1 <
                        len(tempo_changes) else real_tick, real_tick)

        # 计算当前时间点和下一个时间点之间的秒数
        seconds = (next_time - current_time) * \
            current_tempo / (ticks_per_beat * 1000000)

        # 将秒数转换为帧数
        frames = seconds * FPS

        # 累加帧数
        total_frames += frames

    return total_frames


def get_tempo_changes(midiFilePath: str):
    midFile = MidiFile(midiFilePath)
    tick_per_beat: int = midFile.ticks_per_beat
    tempo_changes = []
    for i, track in enumerate(midFile.tracks):
        absolute_time = 0
        for msg in track:
            absolute_time += msg.time
            if msg.type == 'set_tempo':
                tempo_changes.append((i, msg.tempo, absolute_time))
    return tempo_changes, tick_per_beat


def export_midi_info(midiFilePath: str) -> str:
    result = ''
    midFile = MidiFile(midiFilePath)
    for i, track in enumerate(midFile.tracks):
        result += f'Track {i}: {track.name}\n'
        for msg in track:
            if msg.type == 'program_change':
                result += f'Track {i}: {MIDI_INSTRUMENTS[msg.program]}\n'

    return result


def midiToGuitarNotes(midiFilePath: str, useChannel: int = 0, muteChannel: List[int] = [17]) -> object:
    """
    :param muteChannel: channels need to filter out, normally it is drum channel. 需要过滤掉的通道，一般是打击乐通道
    :param midiFilePath: path of input midi file. 输入midi文件路径
    :return: notes and beat in the midi file. 返回midi文件中的音符和拍子
    """
    try:
        midTrack = MidiFile(midiFilePath).tracks[useChannel]
    except:
        midTrack = MidiFile(midiFilePath).tracks[0]

    notes_map = []
    note = []
    real_tick: float = 0

    for message in midTrack:
        ticks = message.time
        real_tick += ticks

        if message.type == 'note_on' and message.time == 0 and message.channel not in muteChannel:
            note.append(message.note)
        else:
            if len(note) == 0:
                continue
            # 将note里的元素按大小排序
            notes = sorted(note)
            notes_map.append({"notes": notes, "real_tick": real_tick})
            note = []

    return notes_map


def processedNotes(chordNotes: list[int], min: int, max: int) -> list[int]:
    """
    :param chordNotes: multiple notes in a chord. 和弦中的多个音符
    :return: simplified notes. 精简后的音符
    """
    compressed = compressNotes(chordNotes, min, max)
    simplified = simplifyNotes(compressed)
    return simplified


def compressNotes(chordNotes: List[int], min: int = 36, max: int = 88) -> List[int]:
    """
    :param chordNotes: input notes. 输入音符
    :param min: minimum note on guitar. 吉他上的最低音符
    :param max: maximum note on guitar. 吉他上的最高音符
    :return: compressed notes. 压缩后的音符
    """
    newChord = []
    for note in chordNotes:
        while note < min:
            note += 12
        while note > max:
            note -= 12
        if note not in newChord:
            newChord.append(note)
    result = sorted(newChord)

    return result


def simplifyNotes(chordNotes: List[int]) -> List[int]:
    """
    :param chordNotes: input notes. 输入音符
    :return: simplified notes. 精简后的音符
    """
    """
    here is the rule of simplifying notes:
    1. if the number of notes is not greater than 6, return the notes directly.    
    2. remove the notes that are octves of the lowest note or the highest note.
    3. if there are still notes need to be removed, randomly remove the notes from the middle notes.
    
    精简音符的规则如下：
    1. 如果音符数量不大于6，直接返回音符。
    2. 移除与最低音或者最高音有八度关系的音符。
    3. 如果还有音符需要移除，随机从中间音符里挑出来需要移除的音符。
    """
    if len(chordNotes) <= 6:
        return chordNotes

    lowestNote = chordNotes[0]
    highestNote = chordNotes[-1]
    middleNotes = chordNotes[1:-2]
    numberOfNotesNeedRemove = len(chordNotes) - 6
    numberOfNoteRemoved = 0

    for note in middleNotes:
        # 如果中间音符与最高音或者最高低有八度关系，可以移除
        if note - lowestNote % 12 == 0 or highestNote - note % 12 == 0:
            middleNotes.remove(note)
            numberOfNoteRemoved += 1
        if numberOfNoteRemoved == numberOfNotesNeedRemove:
            break

    # 如果经过上面的步骤，还有音符需要移除，那么随机从中间音符里挑出来需要移除的音符。
    while numberOfNoteRemoved < numberOfNotesNeedRemove:
        randomIndex = random.randint(0, len(middleNotes) - 1)
        middleNotes.pop(randomIndex)
        numberOfNoteRemoved += 1

    result = [lowestNote] + middleNotes + [highestNote]

    return result


if __name__ == '__main__':
    pass
