
from mido import MidiFile, MidiTrack


def lower_octave(midiFilePath: str, outputFilePath: str):
    """    
    :param midiFilePath: midi文件路径
    :param outputFilePath: 输出文件路径
    useage:将midi文件里所有的音符降八度再另存
    """
    mid = MidiFile(midiFilePath)
    new_mid = MidiFile()

    for i, track in enumerate(mid.tracks):
        new_track = MidiTrack()
        new_mid.tracks.append(new_track)

        for msg in track:
            if msg.type == 'note_on' or msg.type == 'note_off':
                new_msg = msg.copy(note=max(0, msg.note - 12))
                new_track.append(new_msg)
            else:
                new_track.append(msg)

    new_mid.save(outputFilePath)


if __name__ == "__main__":
    input_file = 'G:/fretDance/asset/midi/Polyphonic_tude_No._6_The_Last_Rose_of_Summer_-_H._W._Ernst.mid'
    output_file = f'{input_file[:-4]}_lowered.mid'
    lower_octave(input_file, output_file)
    print("Done!")
