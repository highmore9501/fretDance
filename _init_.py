"""
基本思路：
1.midi文件转化成和弦列表ChordNotes（暂时不考虑时值节拍等问题，只考虑音高和先后顺序）
2.生成一个初始化的左手指型dancer（第一把位，所有手指都在3弦，全部悬空）
3.用初始指型尝试去按第一个和弦ChordNote：

    先得到当前和弦ChordNote所有可能的位置Chord：
        先把和弦里的每个音符note分解成可能的位置position；
            组合所有可能的位置Chords，开始过滤掉不可能在吉它上存在的位置组合，返回过滤后的组合FilteredChords

    对于返回的组合中的每一个位置Chord，求解它所有可能的按法，并返回按法的组合AllDancer;
    对按法组合进行淘汰，只保留前N个消耗行动力最小的dancer。
4.用前步骤得到的所有指型dancer,来处理接下来的和弦，并返回N个dancer
5.依次处理完所有的和弦ChordNotes，返回最终最优的指型dancer,并提取它的轨迹tracer
"""