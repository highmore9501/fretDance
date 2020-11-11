import copy
from collections import Counter


def position(note) -> list:
    """
    计算音符所有可能的位置
    :param note: 音符
    :return: 所有可能的位置集合
    """
    result = []
    resultAppend = result.append
    stringMode = [0, 5, 10, 15, 19, 24]
    for i in range(6):
        string = 6 - i
        fret = note - stringMode[i]
        if 15 >= fret >= 0:
            resultAppend([string, fret])
    return result


def filterDance(allDancer, Limit) -> list:  # 冒泡排序，用来对allDancer里的dancer进行排序，并且删除掉行动力过高的dancer
    length = len(allDancer)
    for i in range(length - 1):
        for j in range(length - 1 - i):  # 第二层for表示具体比较哪两个元素
            if allDancer[j].entropy > allDancer[j + 1].entropy:  # 如果前面的大于后面的，则交换这两个元素的位置
                allDancer[j], allDancer[j + 1] = allDancer[j + 1], allDancer[j]
    if length >= Limit:
        allDancer = allDancer[:Limit - 1]
    return allDancer


def analyzeChord(chordPosition):
    """
    输入和弦位置，返回弦的集合，品的集合
    :param chordPosition: 和弦位置，也即组成和弦的音的按法
    :return: stringList弦的集合，fretList品的集合
    """
    stringList = []
    stringListAppend = stringList.append
    fretList = []
    fretListAppend = fretList.append
    for item in chordPosition:
        stringListAppend(item[0])
        fretListAppend(item[1])
    return stringList, fretList


def listCombination(lists) -> list:
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


def handChordPosition(notePositionList) -> list:
    """
    输入和弦中所有音符可能的位置，输出不重复弦的组合
    :param notePositionList:音符位置组合。

    示范: B和e小三度组合，会呈现为[[[2,0],[3,4],[4,9]],[[1,0],[2,5],[3,9]]]这样的形式，
    其中的[[2,0],[3,4],[4,9]]表示B音的三种可能位置，[[1,0],[2,5],[3,9]]表示e音的三种可能位置
    :return:得到所有可能的音符位置组合。

    示范：B和e小三度组合，最终出来的结果如下，共有9种：
    [[2,0],[1,0]],[[2,0],[2,5]],[[2,0],[3,9]],
    [[3,4],[1,0]],[[3,4],[2,5]],[[3,4],[3,9]],
    [[4,9],[1,0]],[[4,9],[2,5]],[[4,9],[3,9]]

    其中，[[2,0],[2,5]]，[[3,4],[3,9]]因为两个音都在同一根弦上，不可能弹出来，所以被过滤掉。
    """
    result = []
    resultAppend = result.append
    handPositions = listCombination(notePositionList)
    noteNumber = len(notePositionList)
    for handPosition in handPositions:
        strings, frets = analyzeChord(handPosition)
        #  判断当前手型跨品是否正常
        try:
            newFrets = [frets[i] for i in range(0, len(frets)) if frets[i] != 0]
            handWidth = max(newFrets) - min(newFrets)
        except:
            handWidth = 0

        if noteNumber == len(set(strings)) and len(set(frets)) < 5 and handWidth < 5:
            #  没有重复弦；除去空弦外，不重复的品格数小于5；所有品格手指跨度不大于5
            resultAppend(handPosition)

    return result


def arrangeNotesInChord(chordPosition, way):
    """
    :param way: 这个值可以是"string"或者"fret"，表示根据弦或者品来对音符位置进行排序
    :param chordPosition: 输入和弦音符的位置
    :return: 排序过后的音符位置列表,都是由低到的的弦/品进行排列。其中，按品排列的输出结果中，同品位音符的弦的排列，是由低音弦到高音弦的

    示范：一个5品上的Am和弦，原来的音符位置是:
    chordPosition = [[6,5],[5,7],[4,7],[3,5],[2,5],[1,5]]

    把它按"弦"来重排,结果不会变：
    a = arrangeNoteInChord(chordPosition,'string')
    a
    [[6,5],[5,7],[4,7],[3,5],[2,5],[1,5]]

    把它按"品"来重排，结果如下：
    b = arrangeNoteInChord(chordPosition,'fret')
    b
    [[5,7],[4,7],[6,5],[3,5],[2,5],[1,5]]

    之所以对音符位置进行重排，是为了后续处理和弦按法时，明确每个音符要按什么样的顺序来按。
    """
    number = 1
    length = len(chordPosition)
    if way == 'string':
        number = 0
    if type(chordPosition) == tuple:
        ChordList = list(chordPosition)
    else:
        ChordList = chordPosition

    for i in range(length - 1):
        for j in range(length - 1 - i):  # 第二层for表示具体比较哪两个元素
            if ChordList[j][number] > ChordList[j + 1][number]:  # 如果前面的大于后面的，则交换这两个元素的位置
                ChordList[j], ChordList[j + 1] = ChordList[j + 1], ChordList[j]

    return ChordList


def classifyChord(chordPosition):
    """
    :param chordPosition:所有音符的位置，所有音符都是在不同弦上，并且各位置的距离是限制在人类手掌范围内的。
    例如：([6, 5], [5, 7], [4, 7], [3, 5], [2, 5])，表示6弦5品，5弦7品，4弦7品，3弦5品，2弦5品

    :return:和弦类型，是一个列表，用来表示所有非空弦音，从低品到高品对应的个数。
    例如：输入([6, 5], [5, 7], [4, 7], [3, 5], [2, 5])，返回[[5,3],[7,2]]

    和弦分类决定了和弦的处理方式
    """
    frets = []
    for item in chordPosition:
        if item[1] != 0:
            frets.append(item[1])

    return Counter(frets).most_common()


def dancerMaker(dancer, ChordNotes, dancerNumberLimit=200):
    """
    输入初始手型dancer，要按的音符ChordNotes，然后得到按完以后所有可能的手型。
    :param dancer: 初始dancer
    :param ChordNotes: 和弦音符
    :param dancerNumberLimit: 返回的子dancer数量上限
    :return:
    """
    allFretDance = [dancer]
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

    currentDancers = copy.deepcopy(allFretDance)
    currentDancerNumber = len(currentDancers)

    for dancerNumber in range(currentDancerNumber):  # 对所有留存的指法列表遍历
        for handPosition in filteredChordPositions:  # 对所有可能的和弦按法遍历
            currentDancer = copy.deepcopy(allFretDance[dancerNumber])  # 先继承一个父指法
            dancers = currentDancer.handMoveTo(handPosition)  # 用当前指法去按当前和弦的位置，这里会生成多个可能性，需要展开来处理
            allFretDance += dancers  # 加入留存的指法列表
    allFretDance = allFretDance[currentDancerNumber:]  # 删掉父指法
    allFretDance = filterDance(allFretDance, dancerNumberLimit)  # 对指法列表进行排序过滤
    return allFretDance
