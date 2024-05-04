from .GuitarString import GuitarString
from typing import List


class Guitar():
    """
    params:
    guitarStrings: List of guitar strings. 吉他弦列表
    stringDistance: String spacing. 弦间距
    fullString: Length of string. 整根弦的长度
    """

    def __init__(self, guitarStrings: List[GuitarString], stringDistance: float = 0.85, fullString: float = 64.7954):
        self._stringDistance = stringDistance
        self._fullString = fullString
        self.guitarStrings = guitarStrings
        self.harm_notes = self.getHarmonicNotes()

    @property
    def getStringDistance(self) -> float:
        return self._stringDistance

    @property
    def getFullString(self) -> float:
        return self._fullString

    def getHarmonicNotes(self) -> int:
        all_harm_notes = []
        for string in self.guitarStrings:
            base_note = string._baseNote
            string_index = string._stringIndex
            all_harm_notes.append({
                "index": string_index,
                "fret": 5,
                "note": base_note.num + 24
            })
            all_harm_notes.append({
                "index": string_index,
                "fret": 7,
                "note": base_note.num + 19
            })
            all_harm_notes.append({
                "index": string_index,
                "fret": 12,
                "note": base_note.num + 12
            })
            all_harm_notes.append({
                "index": string_index,
                "fret": 4,
                "note": base_note.num + 28
            })
            all_harm_notes.append({
                "index": string_index,
                "fret": 9,
                "note": base_note.num + 28
            })
        return all_harm_notes
