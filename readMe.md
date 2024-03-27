## FretDance

Automatically completes the finger arrangement of guitar music scores, minimizing the movement trajectory of the left hand.

Simple working principle:

1. First, read all the notes from the midi file and treat the simultaneously sounding notes as a chord, and record the time of that chord, which is the beat.
2. Convert each chord into possible positions on the guitar.
3. Consider which fingers to use to press each note, generating all possible fingering shapes.
4. Calculate the cost of transitioning from the current hand shape to the new hand shape.
5. Each time a hand shape is iterated, a recorder is generated to record all previous hand shapes and the cost of reaching the current hand shape. For example, if you start with hand shape a and move to the next chord, there may be three hand shapes b1, b2, b3, then three recorders will be generated to record the costs of a->b1, a->b2, and a->b3, respectively. If you continue to the next step, there may be nine recorders for a->b1->c1, a->b1->c2, a->b1->c3, a->b2->c1, a->b2->c2, a->b2->c3, a->b3->c1, a->b3->c2, and a->b3->c3, respectively.
6. Obviously, you will find that the expansion speed of the recorder is exponential, so we need to prune. The pruning method is to set an upper limit on the number of recorders for each generation, keeping only a certain number of recorders with the smallest cost values, and discarding the others. In the project, we use HandPoseRecordPool to control the number of recorders.
7. Finally, we just need to find a recorder with the smallest cost value and output the recorded hand shape sequence, which is the optimal solution we are looking for.
