def midiToNote(midiFile):
    import mido
    mid = mido.MidiFile(midiFile)
    result = []
    resultAppend = result.append
    note = []
    for msg in mid.play():
        if msg.type == 'note_off' and msg.time != 0:
            if not note:
                note.append(msg.note-40)
            if note:
                resultAppend(note)
                note = []
        if msg.type == 'note_off' and msg.time == 0:
            note.append(msg.note-40)
    return result

