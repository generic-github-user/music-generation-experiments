import playsound
from pydub import AudioSegment
import random

import pygame as pg
import time
import pygame.midi

audio_path = './Middle_C.mp3'
# playsound.playsound(audio_path)

pg.mixer.init()
pg.init()

notes = ['c', 'd', 'a']
sounds = []
for i in range(2):
    note = random.choice(notes)
    note_path = './piano-{}_{}_major.wav'.format(note, note.upper())
    # playsound.playsound(note_path, False)

    sounds.append(pg.mixer.Sound(note_path))

pg.mixer.set_num_channels(20)


# for s in sounds:
#     s.play()

# input()


# pg.midi.init()
# player = pg.midi.Output(0)
# player.set_instrument(0)
#
# player.note_on(60, 127)
# player.note_on(64, 127)
# player.note_on(67, 127)
#
# time.sleep(10)
#
# player.note_off(64, 127)
#
# del player
# pg.midi.quit()


pg.midi.init()
player = pg.midi.Output(0)
player.set_instrument(0)

for i in range(20):
    player.note_on(60+i, 127)
    time.sleep(0.20)

del player
pg.midi.quit()


# TODO: evolved music composition


# sound = AudioSegment.from_file(audio_path)
# octaves = 0.5
# new_sample_rate = int(sound.frame_rate * (2.0 ** octaves))
# chipmunk_sound = sound._spawn(sound.raw_data, overrides={'frame_rate': new_sample_rate})
# chipmunk_ready_to_export = chipmunk_sound.set_frame_rate(44100)

# import soundfile as sf
# import pyrubberband as pyrb
# y, sr = sf.read(audio_path)
# # Play back at double speed
# y_stretch = pyrb.time_stretch(y, sr, 2.0)
# # Play back two semi-tones higher
# y_shift = pyrb.pitch_shift(y, sr, 2)


# import numpy as np
# import sox
# # sample rate in Hz
# sample_rate = 44100
# # generate a 1-second sine tone at 440 Hz
# y = np.sin(2 * np.pi * 440.0 * np.arange(sample_rate * 1.0) / sample_rate)
# # create a transformer
# tfm = sox.Transformer()
# # shift the pitch up by 2 semitones
# tfm.pitch(2)
