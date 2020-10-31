import copy

from calculate import arrangeNotesInChord


def chord2Finger00(dancer):
    """处理[0],输出结果1个,就是完全不动"""
    newDancer = copy.deepcopy(dancer)
    newDancer.trace.append(dancer.trace[-1])
    return newDancer


def chord2Finger01(dancer, Chord):
    """处理[1],输出结果4个,分别用1/2/3/4指单按"""
    result = []
    resultAppend = result.append
    string = Chord[0][0]
    fret = Chord[0][1]

    for i in range(4):
        newDancer = copy.deepcopy(dancer)
        finger = newDancer.allFinger[i]
        newDancer.fingerMoveTo(finger, string, fret)
        resultAppend(newDancer)

    return result


def chord2Finger02(dancer, Chord):
    """处理[2],输出结果3个,输出结果4个,就是1/3/4指大横按或1指小横按,加上输出结果6个,4指对2点组合单按"""
    result = []
    resultAppend = result.append

    newChordByString = arrangeNotesInChord(Chord, 'string')
    newChordByFret = arrangeNotesInChord(Chord, 'fret')
    fret = newChordByString[0][1]
    for i in range(2):  # 1指大小横按
        newDancer = copy.deepcopy(dancer)
        finger = newDancer.allFinger[0]
        newDancer.changeBarre(1, newChordByString[0][0], fret)
        finger.press = i + 2
        resultAppend(newDancer)
    for i in range(2):  # 34指大横按
        newDancer = copy.deepcopy(dancer)
        finger = newDancer.allFinger[i + 2]
        newDancer.changeBarre(i + 2, newChordByString[0][0], fret)
        finger.press = 2
        resultAppend(newDancer)

    from itertools import combinations
    for (finger1, finger2) in combinations([0, 1, 2, 3], 2):  # 1234指对两点单按
        newDancer = copy.deepcopy(dancer)
        newDancer.fingerMoveTo(finger1, newChordByFret[0][0], fret)
        newDancer.fingerMoveTo(finger2, newChordByFret[1][0], fret)
        resultAppend(newDancer)

    return result


def chord2Finger03(dancer, Chord):
    """处理[1,1],输出结果6个,4指对2点组合单按"""
    result = []
    resultAppend = result.append
    newChordByFret = arrangeNotesInChord(Chord, 'fret')

    from itertools import combinations
    for (finger1, finger2) in combinations([0, 1, 2, 3], 2):  # 1234指对两点单按
        newDancer = copy.deepcopy(dancer)
        newDancer.fingerMoveTo(finger1, newChordByFret[0][0], newChordByFret[0][1])
        newDancer.fingerMoveTo(finger2, newChordByFret[1][0], newChordByFret[1][1])
        resultAppend(newDancer)

    return result


def chord2Finger04(dancer, Chord):
    """处理[3],输出结果4个,就是1/3/4指大横按或1指小横按,加上输出结果4个,4指对3点组合单按"""
    result = []
    resultAppend = result.append

    newChordByString = arrangeNotesInChord(Chord, 'string')
    fret = newChordByString[0][1]
    for i in range(2):  # 1指大小横按
        newDancer = copy.deepcopy(dancer)
        finger = newDancer.allFinger[0]
        newDancer.changeBarre(1, newChordByString[0][0], fret)
        finger.press = i + 2
        resultAppend(newDancer)
    for i in range(2):  # 34指大横按
        newDancer = copy.deepcopy(dancer)
        finger = newDancer.allFinger[i + 2]
        newDancer.changeBarre(i + 2, newChordByString[0][0], fret)
        finger.press = 2
        resultAppend(newDancer)

    from itertools import combinations
    for (finger1, finger2) in combinations([0, 1, 2, 3], 3):  # 1234指对三个音单按
        newDancer = copy.deepcopy(dancer)
        newDancer.fingerMoveTo(finger1, newChordByString[0][0], fret)
        newDancer.fingerMoveTo(finger2, newChordByString[1][0], fret)
        newDancer.fingerMoveTo(finger2, newChordByString[2][0], fret)
        resultAppend(newDancer)

    return result


def chord2Finger05(dancer, Chord):
    """处理[2,1],输出结果6个,1指横按/小横按,2/3/4指单按,加上出结果4个,4指对3点组合单按"""
    pass


def chord2Finger06(dancer, Chord):
    """处理[1,2],输出结果2个,3指小横按,1/2指单按,加上输出结果3个,4指小横按,1/2/3指单按,加上出结果4个,4指对3点组合单按"""
    pass


def chord2Finger07(dancer, Chord):
    """处理[1,1,1],输出结果4个,品格从低到高分别用1/2/3/4指,单按3个音"""
    pass


def chord2Finger08(dancer, Chord):
    """处理[4],[5],[6],输出结果1个,就是1指横按"""
    pass


def chord2Finger09(dancer, Chord):
    """处理[1,3],输出结果1个,1指按最低品,2/3/4指根据弦数从低到高单按,加上输出结果2个,3指小横按,1/2指单按,加上输出结果3个,4指小横按,1/2/3指单按"""
    pass


def chord2Finger10(dancer, Chord):
    """处理[2,2],输出结果1个,1/2指按2个低音,3/4指按2个高音,加上输出6个结果,1指大/小横按,23/24/34指单按2个单音,加上输出2个结果,1指大横按,3/4指大横按"""
    pass


def chord2Finger11(dancer, Chord):
    """处理[3,1],[4,1],[5,1]输出结果3个,1指大横按,2/3/4指单按"""
    pass


def chord2Finger12(dancer, Chord):
    """处理[1,1,2],输出结果2个,3/4指大横按,1/2指单按两个音"""
    pass


def chord2Finger13(dancer, Chord):
    """处理[1,2,1],输出结果2个,品格从低到高分别用1234指或1324"""
    pass


def chord2Finger14(dancer, Chord):
    """处理[2,1,1],输出结果6个,1指横按/小横按,2/3/4指按2个单音"""
    pass


def chord2Finger15(dancer, Chord):
    """处理[1,1,1,1],输出结果1个,品格从低到高分别用1/2/3/4指"""
    pass


def chord2Finger16(dancer, Chord):
    """处理[1,4],输出结果4个,3/4指大横按,1/2指单按低音"""
    pass


def chord2Finger17(dancer, Chord):
    """处理[2,3],输出结果2个,1指大横按,3/4指大横按"""
    pass


def chord2Finger18(dancer, Chord):
    """处理[3,2],输出结果2个,1指大横按,3/4指大横按,加上输出6个结果,1指大/小横按,23/24/34指单按2个单音"""
    pass


def chord2Finger19(dancer, Chord):
    """处理[4,2],输出结果2个,1指大横按,3/4指大横按,加上输出3个结果,1指大横按,23/24/34指单按2个单音"""
    pass


def chord2Finger20(dancer, Chord):
    """处理[1,1,3],输出结果2个,3/4指大横按,1/2指单按两个音"""
    pass


def chord2Finger21(dancer, Chord):
    """
    处理[1,1,1,3],输出结果1个,4指大横按,123指按3个单音
    """
    pass


def chord2Finger22(dancer, Chord):
    """处理[2,1,2],输出结果2个,1/4指大横按,2/3指单按1个音,加上输出结果1个,1/3指大横按,2指单按1个音"""
    pass


def chord2Finger23(dancer, Chord):
    """处理[2,2,1],输出结果1个,1/3指大横按,4指单按1个音"""
    pass


def chord2Finger24(dancer, Chord):
    """处理[3,1,1],输出6个结果,1指大/小横按,23/24/34指单按2个单音"""
    pass


def chord2Finger25(dancer, Chord):
    """处理[1,1,1,2],输出结果1个,4指大横按,123指单按3音"""
    pass


def chord2Finger26(dancer, Chord):
    """处理[2,1,1,1],输出结果2个,1指大/小横按,234指单按3音"""
    pass


def chord2Finger27(dancer, Chord):
    """处理[2,1,1,1],输出结果2个,1指大/小横按,234指单按3音"""
    pass


def chord2Finger28(dancer, Chord):
    """处理[3,3],输出结果2个,1指大横按,3/4指大横按,加上输出结果1个,1指大横按,234指单按3音"""
    pass


def chord2Finger29(dancer, Chord):
    """处理[2,4],输出结果2个,1指大横按,3/4指大横按,加上输出6个结果,1指大/小横按,23/24/34指单按2个单音"""
    pass


def chord2Finger30(dancer, Chord):
    """处理[1,5],输出结果3个,1指大横按,2/3/4指单按高音"""
    pass


def chord2Finger31(dancer, Chord):
    """处理[1,1,4],输出结果1个,3指大横按,1/2指单按2个音,加上输出结果3个,4指大横按,12/23/13指按2个音"""
    pass


def chord2Finger32(dancer, Chord):
    """处理[2,1,3],输出结果1个,1/3指大横按,2指单按,加上输出结果2个,1/4指大横按,2/3指单按1个音"""
    pass


def chord2Finger33(dancer, Chord):
    """处理[3,1,2],输出结果1个,1/3指大横按,2指单按,加上输出结果2个,1/4指大横按,2/3指单按1个音"""
    pass


def chord2Finger34(dancer, Chord):
    """处理[4,1,1],输出6个结果,1指大/小横按,23/24/34指单按2个单音"""
    pass


def chord2Finger35(dancer, Chord):
    """处理[2,1,1,2],输出结果1个,1/4指大横按,23指按2个单音"""
    pass


def chord2Finger36(dancer, Chord):
    """处理[3,1,1,1],输出结果2个,1指大/小横按,2/3/4指单按3个音"""
    pass
