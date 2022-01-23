import itertools
import math
import librosa
import numpy as np
from scipy.io import wavfile

SR = 44_100


def get_sin_oscillator(freq=55, amp=1, sample_rate=44100):
    increment = (2 * math.pi * freq) / sample_rate
    return (math.sin(v) * amp for v in itertools.count(start=0, step=increment))


def get_samples(notes_dict, num_samples=256):
    return [
        sum([int(next(osc) * 32767) for _, osc in notes_dict.items()])
        for _ in range(num_samples)
    ]


def get_val(osc, sample_rate=SR):
    return [next(osc) for i in range(sample_rate)]


def getval(osc, count=SR, it=False):
    if it:
        osc = iter(osc)
    # returns 1 sec of samples of given osc.
    return [next(osc) for i in range(count)]


def gettrig(gen, downtime, sample_rate=SR):
    gen = iter(gen)
    down = int(downtime * sample_rate)
    vals = getval(gen, down)
    gen.trigger_release()
    while not gen.ended:
        vals.append(next(gen))
    return vals


def get_seq(osc, notes=["C4", "E4", "G4"], note_lens=[0.5, 0.5, 0.5]):
    samples = []
    osc = iter(osc)
    for note, note_len in zip(notes, note_lens):
        osc.freq = librosa.note_to_hz(note)
        for _ in range(int(SR * note_len)):
            samples.append(next(osc))
    return samples


to_16 = lambda wav, amp: np.int16(wav * amp * (2 ** 15 - 1))


def wave_to_file(wav, wav2=None, fname="temp.wav", amp=0.1):
    wav = np.array(wav)
    wav = to_16(wav, amp)
    if wav2 is not None:
        wav2 = np.array(wav2)
        wav2 = to_16(wav2, amp)
        wav = np.stack([wav, wav2]).T

    wavfile.write(fname, SR, wav)
