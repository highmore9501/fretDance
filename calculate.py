import copy
from collections import Counter


def position(note) -> list:
    """
    计算音符所有可能的位置
    :param note: 音符
    :return: 所有可能的位置集合
    """
    result = []
    resultappend = result.append
    stringMode = [0, 5, 10, 15, 19, 24]
    for i in range(6):
        string = 6 - i
        fret = note - stringMode[i]
        if 12 >= fret >= 0:
            resultappend([string, fret])
    return result


def filterDance(arr, max) -> list:  # 冒泡排序
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
    stringListAppend = stringList.append
    fretList = []
    fretListAppend = fretList.append
    for item in handPosition:
        stringListAppend(item[0])
        fretListAppend(item[1])
    return stringList, fretList


def listsCombiantions(lists) -> list:
    """
    输入多个列表组成的列表，返回多列表中元素的所有可能组合
    :param lists: 多个列表组成的列表
    :return: 所有元素可能的组合
    """
    result = []
    resultAppend = result.append
    from itertools import product
    for i in product(*lists):
        resultAppend(i)
    return result


def handChordPosition(chord) ->list:
    """
    输入和弦中所有音符可能的位置，输出不重复弦的组合
    :param chord:音符组合，示范B和e小三度组合，会呈现为[[[2,0],[3,4],[4,9]],[[1,0],[2,5],[3,9]]]这样的形式，
    其中的[[2,0],[3,4],[4,9]]表示B音的三种可能位置，[[1,0],[2,5],[3,9]]表示e音的三种可能位置
    :return:
    """
    result = []
    resultAppend = result.append
    handPositions = listsCombiantions(chord)
    noteNumber = len(chord)
    for handPosition in handPositions:
        strings, frets = listOfList(handPosition)

        newFrets = [frets[i] for i in range(0,len(frets)) if frets[i]!=0]
        handWidth = max(newFrets) - min(newFrets)
        if noteNumber == len(set(strings)) and len(set(frets)) < 5 and handWidth < 5:
            #  没有重复弦；除去空弦外，不重复的品格数小于5；所有品格手指跨度不大于6
            resultAppend(handPosition)
    return result


class midi2Notes:
    """
    把midi文件里的音符转成数字，只有音高和顺序，没有时值
    """

    def __init__(self, midiFile):
        from mxm.midifile import MidiInFile, MidiToCode
        midiIn = MidiInFile(MidiToCode(), midiFile)
        midiIn.read()


def arrangeNotesInChord(Chord, way):
    """
    :param way: 根据弦高或者品高来排序
    :param Chord: 输入和弦
    :return: 排序过后的音符位置列表,都是由低到的的弦/品进行排列
    其中，按品排列的输出结果中，同品位音符的弦的排列，是由低音弦到高音弦的
    """
    number = 1
    length = len(Chord)
    newChord = list(Chord)
    if way == 'string':
        number = 0

    for i in range(length - 1):
        for j in range(length - 1 - i):  # 第二层for表示具体比较哪两个元素
            if newChord[j][number] > newChord[j + 1][number]:  # 如果前面的大于后面的，则交换这两个元素的位置
                newChord[j], newChord[j + 1] = newChord[j + 1], newChord[j]

    return newChord


def classifyChord(Chord):
    """
    :param Chord:所有音符的位置，所有音符都是在不同弦上，并且各位置的距离是限制在人类手掌范围内的。
    例如：([6, 5], [5, 7], [4, 7], [3, 5], [2, 5])，表示6弦5品，5弦7品，4弦7品，3弦5品，2弦5品

    :return:和弦类型，是一个列表，用来表示所有非空弦音，从低品到高品对应的个数。
    例如：输入([6, 5], [5, 7], [4, 7], [3, 5], [2, 5])，返回[[5,3],[7,2]]

    和弦分类决定了后面对和弦按法的处理
    """
    frets = []
    for item in Chord:
        if item[1] != 0:
            frets.append(item[1])

    return Counter(frets).most_common()


def barreChord(dancer, fingerNumber, Chord):
    """
    处理横按，返回可能的dancer，未完成
    :param dancer:原指型
    :param fingerNumber:横按的手指
    :param Chord:需要按的和弦，已经不存在空弦，而且所有音符都是在不同弦上，并且各位置距离是限制在人类手掌范围内的。
    :return:所有可能的指型
    先计算所有position里的品格，得到列表[[fret1,indexes1],[fret2,indexes2].....]，fret表示品格，indexes是个list，包含同品音符的index。
    """
    from itertools import product
    import copy

    result = []
    resultAppend =result.append
    frets = []
    fretsAppend = frets.append

    for item in Chord:
        fretsAppend(item[1])
    minFret = min(frets)
    minString = min(string for [string, fret] in enumerate(Chord) if fret == minFret)

    if fingerNumber == 1:
        # 先完成横按
        dancer.fingerMoveTo(fingerNumber, minString, minFret)
        # 删掉position里的横按音符
        Chord.remove([string, fret] for [string, fret] in enumerate(Chord) if fret == minFret)
        # 生成其余三指与余下position里的音符所有组合的可能性
        combinations = []
        combinationsAppend = combinations.append
        for i in product([2, 3, 4], Chord):
            combinationsAppend(i)
        # 用所有的组合去完成fingerMoveTo
        for combination in combinations:
            finger = combination[0]
            string = combination[1][0]
            fret = combination[1][1]
            newDancer = copy.deepcopy(dancer)
            newDancer.fingerMoveTo(finger, string, fret)
            resultAppend(newDancer)
    else:
        pass
    return result


def noBarreChord(dancer, position):
    """
    不使用横按，按完所有的音符，返回可能的dancer，未完成
    :param dancer:原指型
    :param position:需要按的和弦，已经不存在空弦，而且所有音符都是在不同弦上，并且各位置距离是限制在人类手掌范围内的。
    :return:所有可能的指型
    """
    result = []
    return result


def dancerMaker(dancer, ChordNotes, dancerNumberLimit=200):
    allFretDance = [dancer]
    allFretDanceAppend = allFretDance.append
    chordPosition = []  # 生成一个空的和弦按法列表
    chordPositionAppend = chordPosition.append

    if len(ChordNotes) > 6:
        print(ChordNotes)
        print('音符超出6个')
        raise

    for note in ChordNotes:  # 把和弦分解成音符
        if note < 0 or note > 48:
            print(ChordNotes)
            print('音符超出上下限')
            raise
        notePositions = position(note)  # 得到当前音符可能的位置列表
        chordPositionAppend(notePositions)  # 得到所有音符的可能的位置列表
    filteredChordPositions = handChordPosition(chordPosition)  # 过滤得到所有无重复弦的音符位置组合，也就是可能的和弦按法组合

    currentDancerNumber = len(allFretDance)

    for dancerNumber in range(currentDancerNumber):  # 对所有留存的指法列表遍历
        for handPosition in filteredChordPositions:  # 对所有可能的和弦按法遍历
            currentDancer = copy.deepcopy(allFretDance[dancerNumber])  # 先继承一个父指法
            dancers = currentDancer.handMoveTo(handPosition)  # 用当前指法去按当前和弦的位置，这里会生成多个可能性，需要展开来处理
            for dancer in dancers:
                if dancer.validation:  # 验证指法是否手指生理要求
                    allFretDanceAppend(dancer)  # 可行则加入留存的指法列表
    allFretDance = allFretDance[currentDancerNumber:]  # 删掉父指法
    allFretDance = filterDance(allFretDance, dancerNumberLimit)  # 对指法列表进行排序过滤
    return allFretDance
