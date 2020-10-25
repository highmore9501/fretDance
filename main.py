"""
需要按一个音符时的处理流程
1.列出有几个点可以按出此音符，乘以四个手指，生成对应个数的dancer()，并且计算并生成消耗点数
2.对所有的dancer继续应用下一个音符，分裂出更多的dancer()，每一个都继承父dancer()的轨迹和消耗点数
3.限制所有dancer()的数量，保持在200以内
"""
import copy

from LeftHand import FretDance
from position import position, filterDance

piece = [19, 24, 27]
fretDance = FretDance()
allFretDance = [fretDance]
dancerNumberLimit = 200

for note in piece:  # 把整个乐曲分解成音符，然后开始遍历
    positions = position(note)  # 得到当前音符可能的按法列表

    for item in positions:  # 分解按法列表
        string = item[0]  # 当前按法的弦数
        fret = item[1]  # 当前按法的品数
        currentDancerNumber = len(allFretDance)
        for dancerNumber in range(currentDancerNumber):  # 对所有留存的指法列表
            for i in range(4):  # 对四个手指都进行遍历
                currentDancer = copy.deepcopy(allFretDance[dancerNumber])
                currentDancer.fingerMoveTo(i, string, fret)  # 用当前手指去按当前音符的位置
                if currentDancer.validation:  # 验证指法是否手指生理要求
                    allFretDance.append(currentDancer)  # 可行则加入留存的指法列表
        allFretDance = allFretDance[currentDancerNumber:]  # 删掉父指法
        allFretDance = filterDance(allFretDance, dancerNumberLimit)  # 对指法列表进行排序过滤

lastDancer = allFretDance[0]
print(lastDancer.trace)
