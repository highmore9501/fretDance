import itertools
import numpy as np
from calculate import arrangeLists


def midiToNoteTypeA(midiFile, muteChannel=None):
    """
    把midi文件转化成乐曲piece，此方法是用来处理不带Note_off的midi文件的
    :param muteChannel:需要去掉的音轨，一般是打击乐。具体音轨需要先看midi文件
    :param midiFile:
    :return: piece
    """
    import mido
    mid = mido.MidiFile(midiFile)
    result = []
    resultAppend = result.append
    note = []
    for msg in mid:
        if msg.type == 'note_on' and msg.channel not in muteChannel:
            if not note:
                note.append(msg.note - 40)
            else:
                if msg.time == 0:
                    note.append(msg.note-40)
                else:
                    notes = list(set(note))
                    resultAppend(notes)
                    note = []
    return result


def midiToNoteTypeB(midiFile, muteChannel=None):
    """
    把midi文件转化成乐曲piece，此方法是用来处理带Note_off的midi文件的
    :param muteChannel:需要去掉的音轨，一般是打击乐。具体音轨需要先看midi文件
    :param midiFile:
    :return: piece
    """
    import mido
    mid = mido.MidiFile(midiFile)

    if not muteChannel:
        muteChannel = [17]
    result = []
    resultAppend = result.append
    note = []
    for msg in mid:
        if msg.type == 'note_on' and msg.channel not in muteChannel:
            note.append(msg.note-40)
        if msg.type == 'note_off' and msg.channel not in muteChannel:
            if note:
                notes = list(set(note))
                resultAppend(notes)
                note = []
    return result


def midiToNote(midiFile, muteChannel=None):
    result = []
    result += midiToNoteTypeB(midiFile, muteChannel)  # 默认存在note_off的方式导出音符，如果不成功则用不存在note_off的方式导出
    if not result:
        result += midiToNoteTypeA(midiFile, muteChannel)

    piece = []  # 对导出的结果进行压缩优化，最到最终结果
    for chord in result:
        piece.append(simplifyChords(chord))
    return piece


def simplifyChords(chordNotes):
    """
    :param chordNotes: 输入和弦
    :return: 返回精简后的和弦
    """
    compressed = compressChord(chordNotes)
    simplified = simplifyChordNote(compressed)
    return simplified


def compressChord(chordNotes):
    """
    压缩和弦中所有音符到0-39之间
    """
    newChord = []
    for note in chordNotes:
        while note < 0:
            note += 12
        while note > 39:
            note -= 12
        newChord.append(note)
    result = list(set(newChord))

    return result


def simplifyChordNote(chordNotes):
    """
    控制音符在6个或以下，精简规律如下：
        1. 8度音优先精简（留下最多11个音符）
        2. 最高音与最低音保留（处理中间9个音符的去留）
        3. 9个音符中提取4个出来，与最高最低音加起来，一共有(9,4)种组合
        4. 计算所有组合中方差最小的，保留。
    """
    chordNotes = arrangeLists(chordNotes)  # 先把音符进行排序

    if len(chordNotes) <= 6:
        return chordNotes
    else:
        middleNotes = chordNotes[1:-2]  # 保留最高音与最低音
        a = middleNotes[:]

        for note in a:  # 去掉和最高音最低音为八度关系的音符
            if (note - chordNotes[0]) % 12 == 0 or (note - chordNotes[-1]) % 12 == 0:
                middleNotes.remove(note)

        length = len(middleNotes)
        b = middleNotes[:]
        for i in range(length - 1):  # 去掉音符中存在八度关系的音符
            for j in range(i+1, length):
                if (b[j] - b[i]) % 12 == 0:
                    middleNotes.remove(middleNotes[i])
                    continue

        filteredNotes = []
        maxDistance = 0
        if len(middleNotes) > 4:  # 如果中间音符数量大于4，从中间音符中选出4个分布最均匀的音符
            for noteList in itertools.combinations(middleNotes, 4):
                minDistances = min([noteList[i+1] - noteList[i] for i in range(3)])
                if minDistances > maxDistance:
                    maxDistance = minDistances
                    if filteredNotes:
                        filteredNotes.append(noteList)
                        filteredNotes = filteredNotes[1:]
                    else:
                        filteredNotes.append(noteList)
        else:
            filteredNotes.append(middleNotes)

        result = [chordNotes[0]]
        result += filteredNotes[0]
        result.append(chordNotes[-1])
        return result


if __name__ == '__main__':
    pass
