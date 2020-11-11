## FretDance
自动完成吉它曲谱的指法编排

名词解释：
* note: 音符，由一个整数表示。在吉他标准调弦的情况下，6弦最低音表示为0，每+1表示加一个半音。因为要适用于吉它，所以和midi中的note值不一样，`note = midiNote - 40`
* chordNote: 组成和弦的所有音符；比如一个由ceg组成的C和弦，可以表示为`[8,12,15]`。在本项目中chordNote的定义和音乐中和弦定义不同在于，一般音乐中和弦是指两个或者以上的音程同时发声；
而本项目中只要是同一时间发出来的声音，无论单音，音程还是和弦，都统称为chordNote。
* notePosition: 音符的位置，由弦数string和品数fret来表示。比如最低音0的位置是`[6,0]`。在吉它上，同一个音经常有几个不同的位置可以弹出来。比如chordNote=12时,notePosition可以是`[6,12],[5,7],[4,2]`
chordPosition: 构成和弦的所有音符的位置，也就是notePosition的列表。比如chordNote=[8,12,15]时，chordPosition可以是`[[6,8],[5,7],[4,5]]`。当然，因为吉它上同一个音可以有不同位置，同一个和弦也会有不同的位置。
所以前面还有`[[5,3],[4,2],[3,0]]`,`[[6,8],[5,7],[3,0]]`也可以用来表示为chordNote=[8,12,15]时的chordPosition。
* piece: 乐曲。乐曲是由一系列的chordNote组成的列表。
* midi: midi格式的音乐文件。经过解析后，midi文件中的音符可以转化成piece，里面只保留了同时发声的音符(chordNote)，以及其发声的先后顺序。midi文件中的其它信息因与指法编排无关，不再保留。
* fretDancer：直译是指板上的舞蹈者，也就是指一只在品格上舞动的左手。它是由四只手指组成（古典吉它中大拇指并不用来按弦，所以不做考虑），可以完成在吉它指板上的各种按弦动作。此外还有两个重要的属性
trace和entropy。trace记录了dancer运动至今的每次动作，每处理一个chordNote时使用的手指finger，按的弦string和品fret，以及是否空弦或大小横按等。
entropy则记录了dancer运动至今每次动作消耗行动力的总和，它的大小意味着dancer运动的省力程度。一般来讲越省力的dancer，它的trace就代表了越科学的指法。
* finger:手指。归属于fretDancer的手指，每个手指都有弦string,品fret,状态press,接触点touchPoint几个属性。表示手指正在几弦几品上，状态press是0/未按或者1/单按，或者是2/大横按，3/小横按。touchPoint
则表示当前手指实际上能按出来的音符位置，可以根据string,fret,press计算得出。


简单运行原理：
1. 先从midi文件中，使用`midiToNote.midiToNote`, 把所有音符读取出来，转成乐曲piece。
2. 生成一个初始化的`LeftHand.fretDance()`，也就是左手的起始位置，默认是左手手指移至3弦，第一把位，全部悬空。
3. fretDance开始运动，去按出piece中第一个chordNote;因为同一个chordNote会有很多可能的位置chordPosition可以按出来，而且同一个chordPosition也可以用不同的手指按法按出来。每一种按法/指法的可能性组合
都会新生成一个子dancer,并且记录下它们实现第一个动作的轨迹trace，以及消耗的行动力entropy。
4. 将所有新生成的子dancer按消耗行动力的大小进行排序，并将生成它们的父dancer删掉。
5. 每个子dancer试图去按下一个chordNote，再生成下一代dancer，并且按消耗行动力排序。依此类推，每处理一个chordNote，dancer就更新换代。
6. 每一代的dancer都设置一个数量上限dancerLimit，排序完以后只留下固定数量的dancer，而将其它行动力过高的删除。*就像生物进化一样，每一代都大量繁殖，但只有固定数量能留存下来，优胜劣汰。*
7. 当所有的chordNote都被按完以后，得到行动力最低的dancer，它的trace就是我们需要的结果。

