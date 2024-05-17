## FretDance

![blender screen capture](https://github.com/highmore9501/fretDance/blob/master/asset/img/image00.png)
Convert the original MIDI file into a guitar tablature fingering arrangement that minimizes the movement trajectories of both hands. Ultimately, present the performance animation in Blender.

Demo video in BiliBili: [https://www.bilibili.com/video/BV1my411Y72J/](https://www.bilibili.com/video/BV1my411Y72J/)
![blender screen capture](https://github.com/highmore9501/fretDance/blob/master/asset/img/20240517043502.png)
![blender screen capture](https://github.com/highmore9501/fretDance/blob/master/asset/img/20240517043331.png)

### How to run

- Install a virtual environment by running `python -m venv .venv`
- Activate the virtual environment by running `source .venv/bin/activate`. For Windows, it is `.\.venv\Scripts\activate`
- Install dependencies by running `pip install -r requirements.txt`
- Run `python main.py`, then select the avatar and midi file in the interface, set the `FPS` and the pitch of each string, and click submit to generate the json data required for the animation.
- Open the corresponding blender file where the avatar is located, go to the `script` interface, select the `animate` file, then copy the absolute paths of the two json files generated in the previous step to the corresponding variables, and click run to generate the animation.
  ![blender script interface](https://github.com/highmore9501/fretDance/blob/master/asset/img/20240517044031.png)

### Simple working principle

1. Read all notes from the MIDI file, treat simultaneously sounding notes as chords, and record the time of the chord.
2. Convert each chord into possible positions on the guitar.
3. Consider which finger to use to press each note, generating all possible fingering hand shapes.
4. Calculate the cost of transitioning from the current hand shape to a new hand shape.
5. Each time a hand shape is iterated, a recorder is generated to record all previous hand shapes and the cost of reaching the current hand shape. For example, at the beginning there is only one hand shape, and pressing the next note may result in 6 new hand shapes, so 6 recorders will be generated. Each recorder records the cost from the original hand shape to the new hand shape. Then when pressing the next note, iterate these 6 new hand shapes again, generating new recorders, and so on.
6. Obviously, you will find that the growth rate of recorders is exponential, so we need pruning. The pruning method is to set an upper limit on the number of recorders for each generation, keeping only a certain number of recorders with the smallest cost values, while discarding other recorders. In the project, we use the size attribute of HandPoseRecordPool to control the number of recorders.
7. Finally, we just need to find a recorder with the smallest cost value, and then output the recorded hand shape sequence from it, which is the optimal solution we are looking for.
8. With the optimal solution for the left hand, we can calculate the optimal solution for the right hand based on this. According to the string to be played each time, calculate the position of the right hand shape and which finger is more scientific to play. The calculation principle is similar to the previous calculation of the left hand shape, which is also continuous iteration, and then controlling the total number of descendants, finally finding the optimal solution.

### Generating animations

Since we already have all the finger information for each time, we can convert this information into keyframe information for controlling hands and arms in Blender files through a series of calculations, thus generating animations.

The basic principles of animation generation are as follows:

1. On the Blender file, read the hand shape information at the four extreme positions of the guitar panel. These four extreme positions are the 1st fret 1st string, 1st fret 6th string, 12th fret 1st string, and 12th fret 6th string.
2. At the above four extreme positions, there are three possible palm angles, corresponding to the NORMAL state when the index finger and middle finger do not press the same fret, the INNER state when the index finger and middle finger press the same fret and the index finger points inward, and the OUTER state when the index finger and middle finger press the same fret and the index finger points outward.
3. By judging the hand shape information at each time, and then interpolating among the data of these extreme positions and corresponding hand shapes, we can obtain a series of controller information for each keyframe, thereby generating animations.
4. The principle of the right hand animation is to determine several possible parking positions for the right palm near the sound hole, and find some possible finger contact positions on the six strings. Each time you want to play, place the corresponding palm and fingers on these playing positions.

In the Blender folder, there are some scripts that run in Blender, which serve the above purposes.

### Other

The purpose of this project is not to output tabs for humans to read, because traditional tabs only record the movement of the left hand fingers that need to be pressed, but lack recording of the positions of the unused left hand fingers.
Of course, for humans, this does not matter, because humans will naturally move their unused fingers to places they feel appropriate.
However, when considering animation generation, which requires the position information of each finger at each keyframe, traditional tabs are not enough.
Therefore, the goal of this project is to output a sequence containing all finger information for each beat, so as to provide sufficient information for animation generation.
