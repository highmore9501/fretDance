KEYNOTES: dict = {
    "C": 48,
    "C#": 49,
    "D": 50,
    "D#": 51,
    "E": 52,
    "F": 53,
    "F#": 54,
    "G": 55,
    "G#": 56,
    "A": 45,
    "A#": 46,
    "B": 47
}


class MusicNote:
    """
    params:
    num: Number of notes, Calculated with C note (3rd fret on the 5th string of standard guitar tuning) as 48. 音符数，以C音（吉它标准调弦的5弦3品）为48来计算
    """

    def __init__(self, num: int) -> None:
        self.num = num
        self.key = self.getKeynote()

    def getKeynote(self):
        """
        :return: keynote such as `C`, `d`, `F1`. 返回像`C`, `d`, `F1`这样的音符
        """
        if hasattr(self, 'key'):
            return self.key
        octave = (self.num-45) // 12
        currentKeynotes = getCurrentKeynotes(octave)
        for key, value in currentKeynotes.items():
            if value == self.num:
                return key

    def add(self, num: int) -> 'MusicNote':
        """
        Add num to the current note.
        :param num: interval of two note, a Major Third count as 4, a Minor Third count as 3. 音程,大三度为4，小三度为3，其它类推
        """
        return MusicNote(self.num + num)


def getCurrentKeynotes(octave: int) -> dict:
    """
    according to the octave, return the current keynotes. 根据八度值返回一个当前的音符字典
    :param octave: 八度
    :return: a dict like KEYNOTES but with diffrent octave. 一个类似KEYNOTES的字典，但是八度不同
    """
    current_keynotes = {}
    for key, value in KEYNOTES.items():
        if octave == 0:
            newkey = key
        elif octave > 0:
            newkey = (key[0] + str(octave) + key[1:]).lower()
        else:
            newkey = key[0] + str(octave) + key[1:]
        current_keynotes[newkey] = value + 12 * octave
    return current_keynotes
