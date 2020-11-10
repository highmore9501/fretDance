def midiToNote(midiFile):
    import mido
    mid = mido.MidiFile(midiFile)
    result = []
    resultAppend = result.append
    note = []
    for msg in mid.play():
        if msg.type == 'note_on':
            note.append(msg.note-40)
        if msg.type == 'note_off':
            if note:
                resultAppend(note)
                note = []
    return result

