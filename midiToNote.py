def midiToNote(midiFile):
    import mido
    mid = mido.MidiFile(midiFile)
    result = []
    resultAppend = result.append
    note = []
    for msg in mid:
        if msg.type == 'note_on':
            note.append(msg.note-40)
        if msg.type == 'note_off':
            if note:
                notes = list(set(note))
                resultAppend(notes)
                note = []
    return result


if __name__ == '__main__':
    midiFile = 'guitarMidiFlies/Aguado_Study_no20.mid'
    piece = midiToNote(midiFile)
    print(piece)

