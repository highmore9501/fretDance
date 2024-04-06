from mido import MidiFile
from typing import List
import random


def midiToGuitarNotes(midiFilePath: str, useChannel: int = 0, muteChannel: List[int] = [17]) -> List[dict]:
    """
    :param muteChannel: channels need to filter out, normally it is drum channel. 需要过滤掉的通道，一般是打击乐通道
    :param midiFilePath: path of input midi file. 输入midi文件路径
    :return: notes and beat in the midi file. 返回midi文件中的音符和拍子
    """
    midFile = MidiFile(midiFilePath)
    tick_per_beat: int = midFile.ticks_per_beat
    midTrack = MidiFile(midiFilePath).tracks[useChannel]
    print(midTrack)

    result = []
    note = []
    time: int = 0

    for message in midTrack:
        time += message.time
        if message.type == 'note_on' and message.time == 0 and message.channel not in muteChannel:
            note.append(message.note)
        else:
            if len(note) == 0:
                continue
            # 将note里的元素按大小排序
            notes = sorted(note)
            beat: float = time / tick_per_beat
            result.append({"notes": notes, "beat": beat})
            note = []
    return result


def processedNotes(chordNotes: list[int]) -> list[int]:
    """
    :param chordNotes: multiple notes in a chord. 和弦中的多个音符
    :return: simplified notes. 精简后的音符
    """
    compressed = compressNotes(chordNotes)
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
