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
        from src.utils.utils import getCurrentKeynotes
        if hasattr(self, 'key'):
            return self.key
        octave = self.num // 12
        keynote = self.num % 12
        currentKeynotes = getCurrentKeynotes(octave)
        for key, value in currentKeynotes.items():
            if value == keynote:
                return key

    def add(self, num: int) -> 'MusicNote':
        """
        Add num to the current note.
        :param num: interval of two note, a Major Third count as 4, a Minor Third count as 3. 音程,大三度为4，小三度为3，其它类推
        """
        return MusicNote(self.num + num)
