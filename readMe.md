## FretDance

Automatically completes the finger arrangement of guitar music scores, minimizing the movement trajectory of the left hand.

### Running Instructions

1. Install the virtual environment by running `python -m venv .venv`
2. Activate the virtual environment by running `source .venv/bin/activate`. For Windows, use `.\.venv\Scripts\activate`
3. Install dependencies by running `pip install -r requirements.txt`
4. Open `FretDancer.ipynb` and set the kernel to `.venv`
5. You can set `midiFilePath` to your own MIDI file path, then run the notebook.
6. In the final `output` method, setting the parameter to `True` will output the positions of fingers that are not pressing strings. If it is not set, the default behavior is to not display the positions of these fingers.

### Simple working principle

1. First, read all the notes from the midi file and treat the simultaneously sounding notes as a chord, and record the time of that chord, which is the beat.
2. Convert each chord into possible positions on the guitar.
3. Consider which fingers to use to press each note, generating all possible fingering shapes.
4. Calculate the cost of transitioning from the current hand shape to the new hand shape.
5. Each time a hand shape is iterated, a recorder is generated to record all previous hand shapes and the cost of reaching the current hand shape. For example, if you start with hand shape a and move to the next chord, there may be three hand shapes b1, b2, b3, then three recorders will be generated to record the costs of a->b1, a->b2, and a->b3, respectively. If you continue to the next step, there may be nine recorders for a->b1->c1, a->b1->c2, a->b1->c3, a->b2->c1, a->b2->c2, a->b2->c3, a->b3->c1, a->b3->c2, and a->b3->c3, respectively.
6. Obviously, you will find that the expansion speed of the recorder is exponential, so we need to prune. The pruning method is to set an upper limit on the number of recorders for each generation, keeping only a certain number of recorders with the smallest cost values, and discarding the others. In the project, we use HandPoseRecordPool to control the number of recorders.
7. Finally, we just need to find a recorder with the smallest cost value and output the recorded hand shape sequence, which is the optimal solution we are looking for.

### Additional Information

The purpose of this project is not to generate tabs for human consumption, as traditional tabs only record the movements of the left hand fingers that need to press the strings. However, they lack information about the positions of the unused left hand fingers.

Of course, for humans, this is not a significant issue, as people naturally move their unused fingers to a comfortable position. However, when considering the generation of animations, where the position information of each finger in every keyframe is required, traditional tabs are insufficient.

Therefore, the goal of this project is to output a sequence containing information about all fingers for each beat, providing enough information for potential animation generation.
