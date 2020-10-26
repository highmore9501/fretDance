def position(note):
    result = []
    stringMode = [0, 5, 10, 15, 19, 24]
    for i in range(6):
        string = 6 - i
        fret = note - stringMode[i]
        if 12 >= fret >= 0:
            result.append([string, fret])
    return result


def filterDance(arr, max):  # 冒泡排序
    length = len(arr)
    if length >= max:
        for i in range(length - 1):
            for j in range(length - 1 - i):  # 第二层for表示具体比较哪两个元素
                if arr[j].entropy > arr[j + 1].entropy:  # 如果前面的大于后面的，则交换这两个元素的位置
                    arr[j], arr[j + 1] = arr[j + 1], arr[j]
        arr = arr[:max - 1]
    return arr


def listOfList(handPosition):
    """
    输入和弦，返回弦的集合，品的集合
    :param handPosition: 和弦，也即组成和弦的音的按法
    :return: stringList弦的集合，fretList品的集合
    """
    stringList = []
    fretList = []
    for item in handPosition:
        stringList.append(item[0])
        fretList.append(item[1])
    return stringList, fretList


def lists_combiantions(lists):
    """
    输入多个列表组成的列表，返回多列表中元素的所有可能组合
    :param lists: 多个列表组成的列表
    :return: 所有元素可能的组合
    """
    result = []
    from itertools import product
    for i in product(*lists):
        result.append(i)
    return result


def handChordPosition(chord):
    """
    输入和弦中所有音符可能的位置，输出不重复弦的组合
    :param chord:音符组合，示范B和e小三度组合，会呈现为[[[2,0],[3,4],[4,9]],[[1,0],[2,5],[3,9]]]这样的形式，
    其中的[[2,0],[3,4],[4,9]]表示B音的三种可能位置，[[1,0],[2,5],[3,9]]表示e音的三种可能位置
    :return:
    """
    result = []
    handPositions = lists_combiantions(chord)
    for handPosition in handPositions:
        strings, frets = listOfList(handPosition)
        try:
            frets.remove(0)
        except:
            pass
        handWidth = max(frets) - min(frets)
        if len(handPosition) == len(set(strings)) and len(set(frets)) < 5 and handWidth < 5:
            #  没有重复弦；除去空弦外，不重复的品格数小于5；所有品格手指跨度不大于6
            result.append(handPosition)
    return result


class midi2Notes:
    """
    把midi文件里的音符转成数字，只有音高和顺序，没有时值
    """

    def __init__(self, midiFile):
        from mxm.midifile import MidiInFile, MidiToCode
        midiIn = MidiInFile(MidiToCode(), midiFile)
        midiIn.read()


if __name__ == '__main__':
    pass
