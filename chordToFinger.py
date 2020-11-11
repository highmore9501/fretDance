from calculate import arrangeNotesInChord


def copyNewDancer(dancer):
    """
    复制原来的dancer，并且把手指都抬起来
    :param dancer:
    :return:
    """
    import copy
    newDancer = copy.deepcopy(dancer)
    newDancer.releaseFingers()
    return newDancer


def getChordList(chordPosition):
    """
    处理和弦音符位置chordPosition，把它分解成需要按的音符位置chordList，和不要按的空弦音noPress，方便后续处理
    :param chordPosition:
    :return:
    """
    chordList = list(chordPosition)
    chordLength = len(chordList)
    noPress = []
    for i in range(chordLength - 1, -1, -1):
        if chordList[i][1] == 0:
            noPress.append(chordList.pop(i))
    return chordList, noPress


def fingerNoteComb(dancer, chordPosition, fingerList, usedFinger=None, ESN=None):
    """
    :param ESN: empty string note 空弦音
    原来母和弦里的空弦音，和这个函数里的Chord不同，这个函数里的Chord已经过滤掉空弦音了
    :param usedFinger: 其它使用过的手指列表
    :param dancer: 原始dancer
    :param chordPosition: 多指需要按的音符位置列表，中间不包含空弦音
    :param fingerList: 可以用到的手指列表，例如[2,3,4]表示利用2/3/4指
    :return: 所有单按完以后生成的dancer列表
    """
    if ESN is None:
        ESN = []
    if usedFinger is None:
        usedFinger = []
    result = []
    resultAppend = result.append
    noteNumber = len(chordPosition)
    realFingerList = fingerList + usedFinger

    from itertools import combinations
    import copy

    for fingerComb in combinations(fingerList, noteNumber):
        newDancer = copy.deepcopy(dancer)
        for i in range(noteNumber):
            newDancer.fingerMoveTo(fingerComb[i], chordPosition[i][0], chordPosition[i][1])
        newDancer.recordTrace(realFingerList, ESN)
        if newDancer.validation(chordPosition):
            resultAppend(newDancer)

    return result


def chord2Finger00(dancer, chordPosition):
    """处理[0],也就是全部空弦音的情况，输出结果1个"""
    newDancer = copyNewDancer(dancer)
    newTrace = []
    for [string, fret] in chordPosition:
        newTrace.append([string, 0])
    newDancer.traceNote.append(newTrace)
    newDancer.traceFinger.append([0])
    return newDancer


def chord2Finger01(dancer, chordPosition):
    """处理[1],输出结果4个,分别用1/2/3/4指单按"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    string = chordList[0][0]
    fret = chordList[0][1]

    for i in range(4):
        newDancer = copyNewDancer(dancer)
        newDancer.fingerMoveTo(i + 1, string, fret)
        newDancer.recordTrace([i + 1], noPress)
        if newDancer.validation(chordPosition):
            resultAppend(newDancer)

    return result


def chord2Finger02(dancer, chordPosition):
    """处理[2],输出结果3个,输出结果4个,就是1/3/4指大横按或1指小横按,
    加上输出结果6个,4指对2点组合单按"""
    result = []
    resultAppend = result.append

    chordList, noPress = getChordList(chordPosition)
    fret = chordList[0][1]
    for i in range(2):  # 1指大横按
        for string in range(chordList[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, fret, i + 2)
            newDancer.recordTrace([1], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    for i in range(2):  # 34指大横按
        for string in range(chordList[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(i + 2, string, fret, 2)
            newDancer.recordTrace([i + 2], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    newDancer = copyNewDancer(dancer)
    singlePressDancer = fingerNoteComb(newDancer, chordPosition, [1, 2, 3, 4], ESN=noPress)  # 1/2/3/4指单按和弦里的2个音
    result += singlePressDancer

    return result


def chord2Finger03(dancer, chordPosition):
    """处理[1,1],输出结果6个,4指对2点组合单按"""
    chordList, noPress = getChordList(chordPosition)
    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    newDancer = copyNewDancer(dancer)
    result = fingerNoteComb(newDancer, newChordByFret, [1, 2, 3, 4], ESN=noPress)
    return result


def chord2Finger04(dancer, chordPosition):
    """处理[3],输出结果4个,就是1/3/4指大横按或1指小横按,
    加上输出结果4个,4指对3点组合单按"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByString = arrangeNotesInChord(chordList, 'string')
    fret = newChordByString[0][1]
    for i in range(2):  # 1指大小横按
        for string in range(newChordByString[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, fret, i + 2)
            newDancer.recordTrace([1], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    for i in range(2):  # 34指大横按
        for string in range(newChordByString[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(i + 2, string, fret, 2)
            newDancer.recordTrace([i + 2], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    newDancer = copyNewDancer(dancer)
    singlePressDancer = fingerNoteComb(newDancer, newChordByString, [1, 2, 3, 4], ESN=noPress)  # 4指对3点组合单按
    result += singlePressDancer

    return result


def chord2Finger05(dancer, chordPosition):
    """处理[2,1],输出结果6个,1指横按/小横按,2/3/4指单按；
    加上出结果4个,4指对3点组合单按"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    fret = newChordByFret[0][1]
    for i in range(2):  # 1指大小横按最低品,2/3/4指单按最高品
        for fingerNumber in range(2, 5):
            for string in range(newChordByFret[0][0], 7):
                newDancer = copyNewDancer(dancer)
                newDancer.changeBarre(1, string, fret, i + 2)
                newDancer.fingerMoveTo(fingerNumber, newChordByFret[2][0], newChordByFret[2][1])
                newDancer.recordTrace([1, fingerNumber], noPress)
                if newDancer.validation(chordPosition):
                    resultAppend(newDancer)

    newDancer = copyNewDancer(dancer)
    singlePressDancer = fingerNoteComb(newDancer, newChordByFret, [1, 2, 3, 4], ESN=noPress)  # 4指对3点组合单按
    result += singlePressDancer

    return result


def chord2Finger06(dancer, chordPosition):
    """处理[1,2],输出结果2个,3指大横按,1/2指单按;
    加上输出结果3个,4指小横按,1/2/3指单按;
    加上出结果4个,4指对3点组合单按"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    fret = newChordByFret[1][1]
    for fingerNumber in range(1, 3):  # 3指大横按，1/2指单按
        for string in range(newChordByFret[1][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(3, string, fret, 2)
            newDancer.fingerMoveTo(fingerNumber, newChordByFret[0][0], newChordByFret[0][1])
            newDancer.recordTrace([3, fingerNumber], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    for fingerNumber in range(1, 4):  # 4指大横按，1/2/3指单按
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(4, string, fret, 2)
            newDancer.fingerMoveTo(fingerNumber, newChordByFret[0][0], newChordByFret[0][1])
            newDancer.recordTrace([4, fingerNumber], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    newDancer = copyNewDancer(dancer)
    singlePressDancer = fingerNoteComb(newDancer, newChordByFret, [1, 2, 3, 4], ESN=noPress)  # 4指对3点组合单按
    result += singlePressDancer

    return result


def chord2Finger07(dancer, chordPosition):
    """处理[1,1,1],输出结果4个,品格从低到高分别用1/2/3/4指,单按3个音"""
    chordList, noPress = getChordList(chordPosition)
    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    newDancer = copyNewDancer(dancer)
    singlePressDancer = fingerNoteComb(newDancer, newChordByFret, [1, 2, 3, 4], ESN=noPress)  # 4指对3点组合单按

    return singlePressDancer


def chord2Finger08(dancer, chordPosition):
    """处理[4],[5],[6],输出结果1个,就是1指横按"""
    chordList, noPress = getChordList(chordPosition)
    for string in range(chordList[0][0], 7):
        newDancer = copyNewDancer(dancer)
        newDancer.changeBarre(1, string, chordList[0][1], 2)
        newDancer.recordTrace([1], noPress)
        if newDancer.validation(chordPosition):
            return newDancer


def chord2Finger09(dancer, chordPosition):
    """处理[1,3],输出结果1个,1指按最低品,2/3/4指根据弦数从低到高单按;
    加上输出结果2个,3指小横按,1/2指单按;加上输出结果3个,4指小横按,1/2/3指单按"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    fret = newChordByFret[1][1]
    for fingerNumber in range(1, 3):  # 3指大横按，1/2指单按
        for string in range(newChordByFret[1][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(3, string, fret, 2)
            newDancer.fingerMoveTo(fingerNumber, newChordByFret[0][0], newChordByFret[0][1])
            newDancer.recordTrace([3, fingerNumber], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    for fingerNumber in range(1, 4):  # 4指大横按，1/2/3指单按
        for string in range(newChordByFret[1][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(4, string, fret, 2)
            newDancer.fingerMoveTo(fingerNumber, newChordByFret[0][0], newChordByFret[0][1])
            newDancer.recordTrace([4, fingerNumber], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    for i in range(1):  # 1234指对四个音单按
        newDancer = copyNewDancer(dancer)
        newDancer.fingerMoveTo(1, newChordByFret[0][0], newChordByFret[0][1])
        newDancer.fingerMoveTo(2, newChordByFret[1][0], fret)
        newDancer.fingerMoveTo(3, newChordByFret[2][0], fret)
        newDancer.fingerMoveTo(4, newChordByFret[2][0], fret)
        newDancer.recordTrace([1, 2, 3, 4], noPress)
        if newDancer.validation(chordPosition):
            resultAppend(newDancer)

    return result


def chord2Finger10(dancer, chordPosition):
    """处理[2,2],输出结果1个,1/2指按2个低音,3/4指按2个高音,
    加上输出6个结果,1指大/小横按,23/24/34指单按2个单音,
    加上输出2个结果,1指大横按,3/4指小横按"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for i in range(0, 1):  # 1指大/小横按,2/3/4指单按2个单音
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], i + 2)
            singlePressDancer = fingerNoteComb(newDancer, newChordByFret[2:], [2, 3, 4], ESN=noPress)
            result += singlePressDancer

    for i in range(0, 1):  # 1指大横按,3/4指小横按
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], 2)
            newDancer.changeBarre(i + 3, newChordByFret[2][0], newChordByFret[2][1], 3)
            newDancer.recordTrace([1, i + 3], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    newDancer = copyNewDancer(dancer)
    for i in range(4):  # 1/2指按2个低音,3/4指按2个高音
        newDancer.fingerMoveTo(i + 1, newChordByFret[i][0], newChordByFret[i][1])
    newDancer.recordTrace([1, 2, 3, 4], noPress)
    if newDancer.validation(chordPosition):
        resultAppend(newDancer)

    return result


def chord2Finger11(dancer, chordPosition):
    """处理[3,1],[4,1],[5,1]输出结果3个,1指大横按,2/3/4指单按"""
    result = []
    chordList, noPress = getChordList(chordPosition)
    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for string in range(newChordByFret[0][0], 7):
        newDancer = copyNewDancer(dancer)  # 1指大横按
        newDancer.changeBarre(1, string, newChordByFret[0][1], 2)
        singlePressDancer = fingerNoteComb(newDancer, [newChordByFret[-1]], [2, 3, 4], ESN=noPress)  # 2/3/4指对1点组合单按
        result += singlePressDancer

    return result


def chord2Finger12(dancer, chordPosition):
    """处理[1,1,2],[1,1,3],输出结果2个,3/4指大横按,1/2指单按两个音"""
    result = []
    chordList, noPress = getChordList(chordPosition)
    newChordByFret = arrangeNotesInChord(chordList, 'fret')

    for i in range(2):
        for string in range(newChordByFret[2][0], 7):
            newDancer = copyNewDancer(dancer)  # 3/4指大横按
            newDancer.changeBarre(i + 3, string, newChordByFret[2][1], 2)
            singlePressDancer = fingerNoteComb(newDancer, [newChordByFret[:1]], [1, 2], ESN=noPress)  # 1,2指对2点组合单按
            result += singlePressDancer

    return result


def chord2Finger13(dancer, chordPosition):
    """处理[1,2,1],[1,1,1,1],输出结果1个,品格从低到高分别用1234"""
    chordList, noPress = getChordList(chordPosition)
    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    newDancer = copyNewDancer(dancer)
    for i in range(4):
        newDancer.fingerMoveTo(i + 1, newChordByFret[i][0], newChordByFret[i][1])
    newDancer.recordTrace([1, 2, 3, 4], noPress)
    if newDancer.validation(chordPosition):
        return newDancer


def chord2Finger14(dancer, chordPosition):
    """处理[2,1,1],[3,1,1],输出结果6个,1指横按/小横按,2/3/4指按2个单音"""
    result = []
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for i in range(0, 1):  # 1指大/小横按,2/3/4指单按2个单音
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], i + 2)
            singlePressDancer = fingerNoteComb(newDancer, newChordByFret[-2:], [2, 3, 4], [1], noPress)
            result += singlePressDancer

    return result


def chord2Finger15(dancer, chordPosition):
    """处理[3,1,1,1],[2,1,1,1],输出结果2个,1指大/小横按,2/3/4指单按3个音"""
    result = []
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for i in range(0, 1):  # 1指大/小横按,2/3/4指单按2个单音
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], i + 2)
            singlePressDancer = fingerNoteComb(newDancer, newChordByFret[i + 2:], [2, 3, 4], [1], noPress)
            result += singlePressDancer

    return result


def chord2Finger16(dancer, chordPosition):
    """处理[1,4],输出结果4个,3/4指大横按,1/2指单按低音"""
    result = []
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for i in range(0, 1):  # 3/4指大横按,1/2指单按低音
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(i + 3, string, newChordByFret[0][1], 2)
            singlePressDancer = fingerNoteComb(newDancer, [newChordByFret[0]], [1, 2], [i + 3], noPress)
            result += singlePressDancer

    return result


def chord2Finger17(dancer, chordPosition):
    """处理[2,3],输出结果2个,1指大横按,3/4指大横按"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for i in range(0, 1):  # 1指大横按,3/4指小横按
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], 2)
            newDancer.changeBarre(i + 3, newChordByFret[2][0], newChordByFret[2][1], 3)
            newDancer.recordTrace([1, i + 3], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    return result


def chord2Finger18(dancer, chordPosition):
    """处理[3,2],输出结果2个,1指大横按,3/4指大横按,
    加上输出6个结果,1指大/小横按,23/24/34指单按2个单音"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for i in range(0, 1):  # 1指大横按,3/4指小横按
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], 2)
            newDancer.changeBarre(i + 3, newChordByFret[2][0], newChordByFret[2][1], 3)
            newDancer.recordTrace([1, i + 3], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    for i in range(0, 1):  # 1指大/小横按,2/3/4指单按2个单音
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], i + 2)
            singlePressDancer = fingerNoteComb(newDancer, newChordByFret[3:], [2, 3, 4], [1], noPress)
            result += singlePressDancer

    return result


def chord2Finger19(dancer, chordPosition):
    """处理[4,2],输出结果2个,1指大横按,3/4指大横按,加上输出3个结果,1指大横按,23/24/34指单按2个单音"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for string in range(newChordByFret[0][0], 7):
        newDancer = copyNewDancer(dancer)
        newDancer.changeBarre(1, string, newChordByFret[0][1], 2)
        singlePressDancer = fingerNoteComb(newDancer, newChordByFret[4:], [2, 3, 4], [1], noPress)
        result += singlePressDancer

    for i in range(0, 1):  # 1指大横按,3/4指小横按
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], 2)
            newDancer.changeBarre(i + 3, newChordByFret[4][0], newChordByFret[4][1], 3)
            newDancer.recordTrace([1, i + 3], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    return result


def chord2Finger20(dancer, chordPosition):
    """处理[2,1,1,2],输出结果1个,1指大横按，4指小横按,23指按2个单音"""
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for string in range(newChordByFret[0][0], 7):
        newDancer = copyNewDancer(dancer)
        newDancer.changeBarre(1, string, newChordByFret[0][1], 2)
        newDancer.changeBarre(4, newChordByFret[4][0], newChordByFret[4][1], 3)
        newDancer.fingerMoveTo(2, newChordByFret[2][0], newChordByFret[2][1])
        newDancer.fingerMoveTo(3, newChordByFret[3][0], newChordByFret[3][1])
        newDancer.recordTrace([1, 2, 3, 4], noPress)
        if newDancer.validation(chordPosition):
            return newDancer


def chord2Finger21(dancer, chordPosition):
    """
    处理[1,1,1,3],输出结果1个,4指小横按,123指按3个单音
    """
    result = []
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for string in range(newChordByFret[0][0], 7):
        newDancer = copyNewDancer(dancer)
        newDancer.changeBarre(4, string, newChordByFret[3][1], 3)
        newDancer.fingerMoveTo(1, newChordByFret[0][0], newChordByFret[0][1])
        newDancer.fingerMoveTo(2, newChordByFret[1][0], newChordByFret[1][1])
        newDancer.fingerMoveTo(3, newChordByFret[2][0], newChordByFret[2][1])
        newDancer.recordTrace([1, 2, 3, 4], noPress)
        if newDancer.validation(chordPosition):
            return result


def chord2Finger22(dancer, chordPosition):
    """处理[2,1,2],输出结果2个,1指大横按，4指小横按,2/3指单按1个音,
    加上输出结果1个,1/3指大横按,2指单按1个音"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for string in range(newChordByFret[0][0], 7):
        newDancer = copyNewDancer(dancer)
        newDancer.changeBarre(1, string, newChordByFret[0][1], 2)  # 1指大横按，4指小横按,2/3指单按1个音
        newDancer.changeBarre(4, newChordByFret[3][0], newChordByFret[3][1], 3)
        singlePressDancer = fingerNoteComb(newDancer, [newChordByFret[2]], [2, 3], [1, 4], noPress)
        result += singlePressDancer

    for i in range(1):  # 1指大横按，3指小横按,2指单按1个音
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], 2)
            newDancer.changeBarre(3, newChordByFret[3][0], newChordByFret[3][1], 3)
            newDancer.fingerMoveTo(2, newChordByFret[2][0], newChordByFret[2][1])
            newDancer.recordTrace([1, 2, 3], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    return result


def chord2Finger23(dancer, chordPosition):
    """处理[2,2,1],输出结果1个,1指大横按，3指小横按,4指单按1个音
    加上输出结果2个，1指大/小横按，2/3/4指按3个音"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for string in range(newChordByFret[0][0], 7):
        newDancer = copyNewDancer(dancer)
        newDancer.changeBarre(1, string, newChordByFret[0][1], 2)  # 1指大横按，3指小横按,4指单按1个音
        newDancer.changeBarre(3, newChordByFret[2][0], newChordByFret[2][1], 3)
        newDancer.fingerMoveTo(4, newChordByFret[4][0], newChordByFret[4][1])
        newDancer.recordTrace([1, 3, 4], noPress)
        if newDancer.validation(chordPosition):
            resultAppend(newDancer)

    for i in range(2):
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], i + 2)  # 1指大/小横按，2/3/4指按3个音
            newDancer.fingerMoveTo(2, newChordByFret[2][0], newChordByFret[2][1])
            newDancer.fingerMoveTo(3, newChordByFret[3][0], newChordByFret[3][1])
            newDancer.fingerMoveTo(4, newChordByFret[4][0], newChordByFret[4][1])
            newDancer.recordTrace([1, 2, 3, 4], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    return result


def chord2Finger24(dancer, chordPosition):
    """处理[4,1,1],输出3个结果,1指大横按,23/24/34指单按2个单音"""
    result = []
    chordList, noPress = getChordList(chordPosition)
    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for string in range(newChordByFret[0][0], 7):
        newDancer = copyNewDancer(dancer)
        newDancer.changeBarre(1, string, newChordByFret[0][1], 2)
        singlePressDancer = fingerNoteComb(newDancer, newChordByFret[-2:], [2, 3, 4], [1], noPress)
        result += singlePressDancer

    return result


def chord2Finger25(dancer, chordPosition):
    """处理[1,1,1,2],输出结果1个,4指大横按,123指单按3音"""
    result = []
    chordList, noPress = getChordList(chordPosition)
    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for string in range(newChordByFret[3][0], 7):
        newDancer = copyNewDancer(dancer)  # 4指大横按
        newDancer.changeBarre(4, string, newChordByFret[3][1], 2)
        singlePressDancer = fingerNoteComb(newDancer, [newChordByFret[:2]], [1, 2, 3], [4], noPress)  # 1/2/3指对3点组合单按
        result += singlePressDancer

    return result


def chord2Finger26(dancer, chordPosition):
    """处理[3,1,2],输出结果1个,1指大横按，3指小横按,2指单按,
    加上输出结果2个,1指大横按，4指小横按,2/3指单按"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for string in range(newChordByFret[0][0], 7):
        newDancer = copyNewDancer(dancer)
        newDancer.changeBarre(1, string, newChordByFret[0][1], 2)  # 1指大横按，3指小横按,2指单按
        newDancer.changeBarre(3, newChordByFret[-2][0], newChordByFret[-2][1], 3)
        newDancer.fingerMoveTo(2, newChordByFret[3][0], newChordByFret[3][1])
        newDancer.recordTrace([1, 2, 3], noPress)
        if newDancer.validation(chordPosition):
            resultAppend(newDancer)

    for i in range(2):
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], 2)  # 1指大横按，4指小横按,2/3指单按
            newDancer.changeBarre(4, newChordByFret[-2][0], newChordByFret[-2][1], 3)
            newDancer.fingerMoveTo(i + 2, newChordByFret[3][0], newChordByFret[3][1])
            newDancer.recordTrace([1, 4, i + 2], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    return result


def chord2Finger27(dancer, chordPosition):
    """处理[2,1,3],输出结果2个,1指大/小横按，3指小横按,2指单按,
    加上输出结果2个,1/4指大横按,2/3指单按1个音"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for i in range(2):
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], i + 2)  # 1指大/小横按，3指小横按,2指单按
            newDancer.changeBarre(3, newChordByFret[-2][0], newChordByFret[-2][1], 3)
            newDancer.fingerMoveTo(2, newChordByFret[2][0], newChordByFret[2][1])
            newDancer.recordTrace([1, 2, 3], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    for i in range(2):
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], 2)  # 1指大横按,4指小横按，2/3指单按1个音
            newDancer.changeBarre(4, newChordByFret[-2][0], newChordByFret[-2][1], 3)
            newDancer.fingerMoveTo(i + 2, newChordByFret[2][0], newChordByFret[2][1])
            newDancer.recordTrace([1, 4, i + 2], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    return result


def chord2Finger28(dancer, chordPosition):
    """处理[3,3],输出结果2个,1指大横按,3/4指大横按,
    加上输出结果1个,1指大横按,234指单按3音"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for string in range(newChordByFret[0][0], 7):
        newDancer = copyNewDancer(dancer)
        newDancer.changeBarre(1, string, newChordByFret[0][1], 2)  # 1指大横按,234指单按3音
        singlePressDancer = fingerNoteComb(newDancer, newChordByFret[3:], [2, 3, 4], [1], noPress)
        result += singlePressDancer

    for i in range(0, 1):  # 1指大横按,3/4指小横按
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], 2)
            newDancer.changeBarre(i + 3, newChordByFret[3][0], newChordByFret[3][1], 3)
            newDancer.recordTrace([1, i + 3], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    return result


def chord2Finger29(dancer, chordPosition):
    """处理[2,4],输出结果1个,1指大横按,3/4指小横按"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')

    for i in range(2):  # 1指大横按,3/4指小横按
        for string in range(newChordByFret[0][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(1, string, newChordByFret[0][1], 2)
            newDancer.changeBarre(i + 3, newChordByFret[2][0], newChordByFret[2][1], 2)
            newDancer.recordTrace([1, i + 3], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    return result


def chord2Finger30(dancer, chordPosition):
    """处理[1,5],输出结果2个,1指单按,3/4指小横按"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')

    for i in range(2):  # 1指单按,3/4指小横按
        for string in range(newChordByFret[1][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(i + 3, string, newChordByFret[1][1], 3)
            newDancer.fingerMoveTo(1, newChordByFret[0][0], newChordByFret[0][1])
            newDancer.recordTrace([1, i + 3], noPress)
            if newDancer.validation(chordPosition):
                resultAppend(newDancer)

    return result


def chord2Finger31(dancer, chordPosition):
    """处理[1,1,4],输出结果1个,3指小横按,1/2指单按2个音,
    加上输出结果3个,4指大横按,12/23/13指按2个音"""
    result = []
    resultAppend = result.append
    chordList, noPress = getChordList(chordPosition)

    newChordByFret = arrangeNotesInChord(chordList, 'fret')
    for string in range(newChordByFret[2][0], 7):
        newDancer = copyNewDancer(dancer)
        newDancer.changeBarre(3, string, newChordByFret[2][1], 3)  # 3指小横按,1/2指单按2个音
        for i in range(2):
            newDancer.fingerMoveTo(i + 1, newChordByFret[i][0], newChordByFret[i][1])
        newDancer.recordTrace([1, 2, 3], noPress)
        if newDancer.validation(chordPosition):
            resultAppend(newDancer)

    for i in range(1):
        for string in range(newChordByFret[2][0], 7):
            newDancer = copyNewDancer(dancer)
            newDancer.changeBarre(4, string, newChordByFret[2][1], 3)  # 4指小横按,1/2/3指按2个音
            singlePressDancer = fingerNoteComb(newDancer, newChordByFret[:1], [1, 2, 3], [4], noPress)
            result += singlePressDancer

    return result
