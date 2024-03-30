from .GuitarString import GuitarString
from .MusicNote import MusicNote


class GuitarNote:
    """
    params:
    guitarString: GuitarString object. 吉他弦对象
    fret: Fret number. 品位
    """

    def __init__(self, guitarString: GuitarString, fret: int):
        self._guitarString = guitarString
        self._fret = fret
        self.note = self.getNote()

    def getNote(self) -> MusicNote:
        if self.note:
            return self.note
        return self._guitarString.baseNote.addKey(self._fret)
