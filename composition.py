import pygame as pg
from itertools import chain
import copy
import random

from note import *
from pitch import *
from melody import *
from chord import *
from scale import *

class Composition:
    """A musical arrangement that brings together Melodies and properties such as a key signature, common tempo, etc."""
    def __init__(self, key='B_,E_', instrument=0):
        pg.midi.init()
        self.player = pg.midi.Output(0)
        self.p = self.player

        self.notes = 'C,C^/D_,D,D^/E_,E,F,F^/G_,G,G^/A_,A,A^/B_,B'
        self.notes = [n.split('/') for n in self.notes.split(',')]
        self.base_notes = list('CDEFGAB')
        print(self.notes)

        self.player.set_instrument(instrument)
        self.key = key.split(',')
        self.key_notes = [n[0] for n in self.key]

        self.accidentals = {
            '^': 1,
            '_': -1
        }

        self.tempo: int = 120
        """The tempo of the piece in beats per minute"""


        self.main_melody = Melody(key=self.key)
        print(self.main_melody.sequence)

    def gen(self, current=0, depth=5, pls=None, reuse_prob=None, reverse_prob=None, shift_prob=None, passes=2):

        new_section = Melody(key=self.key)
        pl = random.randint(*pls[current])
        print(pl)
        if current < depth:
            potential_melodies = self.sections_[current]
            # Randomly select an existing melody from this level of the tree
            if random.uniform(0,1) < reuse_prob[current] and len(potential_melodies) > 0 and depth > 3:
                # does this need to be cloned?
                rep_section = random.choice(potential_melodies)#.clone()
                for b in range(pl):
                    new_section.add(rep_section)
            # Otherwise, create a new melody (and submelodies, possibly) and add to the list
            else:
                # ?
                for b in range(pl // 2 + 1):
                    subsection = self.gen(current=current+1, pls=pls, reuse_prob=reuse_prob, reverse_prob=reverse_prob, depth=depth, shift_prob=shift_prob)
                    new_section.add(subsection)
                    self.sections_[current].append(subsection)

        # Bottom level is reached
        elif current == depth:
            # does this need to be turned off ?
            new_section = Melody(key=self.key).randomize(length=pl)


        if random.uniform(0,1) < reverse_prob[current]:
            new_section.reverse()

        if random.uniform(0,1) < shift_prob[current]:
            new_section.shift(random.randint(-1, 1))

            # alternatively, randomly select for each bottom-level melody it should be newly generated
            # TODO: reverse some sections
        return new_section

    def generate(self, part_lengths=[(1,5), (1,5), (1,5), (3,5), (2,5), (2,6)], reuse_prob=[0.3]*6, reverse_prob=[0.3]*6, shift_prob=[0.1]*6, method='iterative', flatten=False, play=False, tempo=(50, 150, 'uniform'), velocity=(100, 127, 'uniform'), scale_steps=(4,8), scale_skip=(1,3), segments=(20, 20, 20), reverse=0.2, shift=0.0, shift_size=2, sample_length=(2,6), target=60, max=1000):
        """Generate a random piece of music based on a set of structural parameters"""

        depth = 5
        self.sections_ = [[] for d in range(depth)]

        # Recursively generate new sub-melodies to the desired depth, randomly creating new ones on the fly
        if method == 'recursive':
            self.main_melody.add(self.gen(pls=part_lengths, depth=depth, reuse_prob=reuse_prob, reverse_prob=reverse_prob, shift_prob=shift_prob))
            print(self.main_melody.sequence[0].sequence[0].sequence[0].sequence)
            print([len(h) for h in self.sections_])
            self.main_melody.print_tree()
        # Generate a few samples, combine them randomly, then generate the piece start-to-finish
        elif method == 'iterative':
            self.samples = []
            comb_length = (2, 4)

            # Generate the base melodies that will be combined into longer sequences
            for v in range(segments[0]):
                # Randomly choose whether to create a random melody or a scale
                if random.uniform(0,1) < 0.6:
                    new_sample = Melody(key=self.key).randomize(length=random.randint(*sample_length), chord=True, tempo=tempo, velocity=velocity)
                else:
                    new_sample = Scale(start=(30,40), steps=scale_steps, use_chord='rand', chord_size=(2,5), skip=scale_skip, key=self.key, player=self.p, note_length=(1/16,1/2), velocity=velocity, dirs='rand')
                self.samples.append(new_sample)

            # Combine the melodies generated above into longer sequences (which are then added to the list and can be randomly selected, allowing nesting of melodies)
            for g in range(segments[1]):
                numsamples = random.randint(*comb_length)
                subsamples = random.choices(self.samples, k=numsamples)

                # If flatten is True, extract submelodies before creating combined melody
                if flatten:
                    combined = Melody([item for sublist in subsamples for item in sublist.sequence], key=self.key)
                # Otherwise, use nested melodies
                else:
                    combined = Melody(subsamples, key=self.key)

                # Randomly decide whether to reverse section
                if random.uniform(0,1) < reverse:
                    combined.reverse()

                # Randomly decide whether to shift section
                if random.uniform(0,1) < shift:
                    combined.shift(random.randint(-shift_size, shift_size))

                self.samples.append(combined)

            self.melody_sequence = Melody(key=self.key)

            # Determine number of times to attempt adding a melody
            if target and max:
                rep = max
            elif segments:
                rep = segments[2]

            for r in range(rep):
                # Choose a random sample
                rand_sample = random.choice(self.samples)
                # Randomly repeat sample between 1 and 4 times
                for x in range(random.randint(1,4)):
                    self.melody_sequence.add(rand_sample)

                # Stop if composition length target is met or exceeded
                if self.melody_sequence.time() >= target:
                    break

            self.main_melody = self.melody_sequence
            self.main_melody.print_tree()
            print(self.main_melody.time())
            print(self.samples)

            # print([v.notes[0].pitch.note_name for v in self.scale(start=random.randint(30,40), steps=random.randint(4,16), skip=1, use_chord=True).shift(1).sequence])
            # print([v.notes[0].pitch.midi for v in self.scale(start=random.randint(30,40), steps=random.randint(4,16), skip=1, use_chord=True).shift(0).sequence])
            #
            # print([v.pitch.note_name for v in self.scale(start=random.randint(30,40), steps=random.randint(4,16), skip=1, use_chord=False).shift(1).sequence])
            # print([v.pitch.midi for v in self.scale(start=random.randint(30,40), steps=random.randint(4,16), skip=1, use_chord=False).shift(0).sequence])

            # TODO: melody combination method
            # TODO: overlaying multiple melodies (alternate, merge, etc.)
        else:
            print('Unknown generation method: '+method)

        if play:
            self.play_()

        # breakpoint()

    def play_(self):
        self.play_melody(self.main_melody)

    def midi_note(self, note_name, octave=None):
        nn = note_name.split('.')
        if len(nn) > 1:
            octave = int(nn[1])
        nn = nn[0]
        for i, note in enumerate(self.notes):
            if nn in note:
                base = ((octave + 2) * len(self.notes)) + i
                if nn in self.key_notes:
                    base += self.accidentals[self.key[self.key_notes.index(nn)]]
                print((nn, base))
                return base
        return -1

    def note_name(self, midi, simple=False):
        k = 12
        # print(self.notes[(midi % k)])
        return '/'.join(self.notes[(midi % k)]) + '.' + str(midi // k)

    # print(midi_note('D',8))

    def play_note(self, note, velocity=127):
        if type(note) is int:
            # base = self.get_base(pitch)
            base = round(note * (2/3))
            base = self.get_base(base)
            # print(base)
            if base in self.key_notes:
                note += self.accidentals[self.key[self.key_notes.index(base)][1]]
            print((self.note_name(note), note))
            self.player.note_on(note, velocity)
        elif type(note) is Note:
            # self.player.note_on(note.pitch.midi, note.velocity)
            note.update_key(self.key)
            note.info()
            note.play()
        elif type(note) is Chord:
            note.play()

    def adjust_pitch(self, note):
        if any([((note - m) % 12 == 0) for m in (1, 3, 6, 8, 10)]):
            print(True)
            note -= 1
        return note

    def chord(self, start, num=3):
        if type(start) is str:
            start = self.midi_note(start)

        for n in range(num):
            # self.player.note_on(start+(2*n), 127)
            pitch = start + (2 * n)
            self.player.note_on(self.adjust_pitch(pitch), 127)

    def get_base(self, pitch):
        rel_index = (pitch + 0) % len(self.base_notes)
        base = self.base_notes[rel_index]
        print((base, pitch))
        return base

    def play_melody(self, melody):
        melody.play(self.player)

    def repeat_melody(self, melody, n, offset=0):
        """Repeat a melody x times"""
        # parent_melody = Melody([melody] * n)
        parent_melody = Melody([melody.clone().step(offset*j) for j in range(n)], key=self.key)
        self.play_melody(parent_melody)

    def play(self, content):
        if type(content) is Melody:
            self.play_melody(content)
        elif type(content) is Note:
            self.play_note(content)
        # self.play chord?

    # TODO: chord constructor? (would inherit key, tempo, etc. from parent composition)
    # recommended style/convention for subclass constructors?

    def demo(self):
        k_ = self.key
        Chord('C.3', custom=[1,5], player=self.p, key=k_).play()
        Chord('C.3', custom=[3,7], player=self.p, key=k_).play()

        # double-check these
        Chord('C.3', interval=(0, 6, 1), player=self.p, key=k_).play()
        Chord('C.3', interval=(0, 6, 2), player=self.p, key=k_).play()

        Chord(Pitch(30, ptype='natural'), player=self.p, key=k_, num=3).play()
        Chord(Pitch(30, ptype='natural'), player=self.p, key=k_, num=5).play()
        Chord(Pitch(32, ptype='natural'), player=self.p, key=k_, num=3).play()

        Chord('C.3', player=self.p).play()

        time.sleep(1)
        # self.scale('B_.2', 8, velocity=126, note_length=0.2, use_chord=False)
        for i in range(1, 5):
            print('Playing chord with {} simultaneous notes'.format(i))
            self.scale('B_.2', 8, velocity=126, note_length=0.2, use_chord=True, chord_size=i, play=True)
            time.sleep(1)

        time.sleep(5)

    # scale(60, 20)


    # chord('C.3', 3)

    def end(self):
        """Clean up pygame midi handlers"""
        del self.player
        pg.midi.quit()
