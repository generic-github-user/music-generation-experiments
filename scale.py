from itertools import chain

from melody import *

class Scale(Melody):
    def __init__(self, start, steps, velocity=127, note_length=1/4, use_chord=False, chord_size=3, play=False, skip=1, key=None, player=None):
        """Generate a scale given a starting point, number of steps, and information about each note"""

        assert key is not None
        assert player is not None
        self.key = key
        self.player = player
        self.p = self.player
        super().__init__(key=self.key, player=self.player)

        default_args = {
            'start': 40,
            'steps': 8,
            'velocity': 127,
            'chord_size': 3,
            'play_scale': False,
            'skip': 1,
            'use_chord': False,
            'note_length': 1/4
        }
        if type(start) is Pitch:
            start = Note(start, ptype='natural', key=self.key)
        elif type(start) is int:
            start = Note(Pitch(start, ptype='natural'), key=self.key)
        elif type(start) is str:
            start = Note(start, key=self.key)

        start = start.pitch.nat

        for i in list(chain(range(0, steps, skip), range(steps, -1, -skip))):
            if use_chord:
                scale_note = Chord(Pitch(start+i,ptype='natural'), player=self.p, key=self.key, length=note_length, num=chord_size)
            else:
                scale_note = Note(Pitch(start+i, ptype='natural'), player=self.p, key=self.key, length=note_length)

            self.add(scale_note)

        if play:
            self.play()