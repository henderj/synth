from abc import ABC, abstractmethod
import itertools
import math


class Oscillator(ABC):
    def __init__(
        self,
        frequency=440,
        phase=0,
        amplitude=1,
        sample_rate=44_100,
        wave_range=(-1, 1),
    ) -> None:
        self._frequency = frequency
        self._phase = phase
        self._amplitude = amplitude
        self._sample_rate = sample_rate
        self._wave_range = wave_range

        self._f = frequency
        self._a = amplitude
        self._p = phase

    @property
    def init_frequency(self):
        return self._frequency

    @property
    def init_amplitude(self):
        return self._amplitude

    @property
    def init_phase(self):
        return self._phase

    @property
    def frequency(self):
        return self._f

    @property.setter
    def frequency(self, value):
        self._f = value
        self._post_frequency_set()

    @property
    def amplitude(self):
        return self._a

    @property.setter
    def amplitude(self, value):
        self._a = value
        self._post_amplitude_set()

    @property
    def phase(self):
        return self._p

    @property.setter
    def phase(self, value):
        self._p = value
        self._post_phase_set()

    def _post_frequency_set(self):
        pass

    def _post_amplitude_set(self):
        pass

    def _post_phase_set(self):
        pass

    @abstractmethod
    def _initialize_oscillator(self):
        pass

    @staticmethod
    def squish_value(value, min_value=0, max_value=1):
        return (((value + 1) / 2) * (max_value - min_value)) + min_value

    @abstractmethod
    def __next__(self):
        return None

    def __iter__(self):
        self.frequency = self._frequency
        self.phase = self._phase
        self.amplitude = self._amplitude
        self._initialize_oscillator()
        return self


class SineOscillator(Oscillator):
    def _post_frequency_set(self):
        self._step = (2 * math.pi * self._f) / self._sample_rate

    def _post_phase_set(self):
        self._p = (self.p / 360) * 2 * math.pi

    def _initialize_oscillator(self):
        self._i = 0

    def __next__(self):
        val = math.sin(self._i + self._p)
        self._i = self._i + self._step
        if self._wave_range is not (-1, 1):
            val = self.squish_value(val, *self._wave_range)
        return val * self._a


class SquareOscillator(SineOscillator):
    def __init__(
        self,
        frequency=440,
        phase=0,
        amplitude=1,
        sample_rate=44100,
        wave_range=(-1, 1),
        threshold=0,
    ) -> None:
        super().__init__(frequency, phase, amplitude, sample_rate, wave_range)
        self.threshold = threshold

    def __next__(self):
        val = math.sin(self._i + self._p)
        self._i = self._i + self._step
        if val < self.threshold:
            val = self._wave_range[0]
        else:
            val = self._wave_range[1]
        return val * self._a


class SawtoothOscillator(Oscillator):
    def _post_frequency_set(self):
        self._period = self._sample_rate / self._f
        self._post_phase_set()

    def _post_phase_set(self):
        self._p = ((self._p + 90) / 360) * self._period

    def _initialize_oscillator(self):
        self._i = 0

    def __next__(self):
        div = (self._i + self._p) / self._period
        val = 2 * (div - math.floor(0.5 + div))
        self._i += 1
        if self._wave_range is not (-1, 1):
            val = self.squish_value(val, *self._wave_range)
        return val * self._a


class TriangleOscillator(SawtoothOscillator):
    def __next__(self):
        div = (self._i + self._p) / self._period
        val = 2 * (div - math.floor(0.5 + div))
        val = (abs(val) - 0.5) * 2
        self._i = self._i + 1
        if self._wave_range is not (-1, 1):
            val = self.squish_val(val, *self._wave_range)
        return val * self._a


class WaveAdder:
    def __init__(self, *oscillators) -> None:
        self.oscillators = oscillators
        self.n = len(oscillators)

    def __iter__(self):
        [iter(osc) for osc in self.oscillators]
        return self

    def __next__(self):
        return sum(next(osc) for osc in self.oscillators) / self.n

from scipy.io import wavefile
import numpy as np
import librosa

SR = 44_100


def get_val(osc, sample_rate=SR):
    return [next(osc) for i in range(sample_rate)]

def get_seq(osc, notes=["C4", "E4", "G4"], note_lens=[0.5,0.5,0.5]):
    samples = []
    osc = iter(osc)
    for note, note_len in zip(notes, note_lens):
        osc.freq = librosa.note_to_hz(note)
        for _ in range(int(SR * note_len)):
            samples.append(next(osc))
    return samples

to_16 = lambda wav, amp: np.int16(wav * amp * (2**15 - 1))
def wave_to_file(wav, wav2=None, fname="temp.wav", amp=0.1):
    wav = np.array(wav)
    wav = to_16(wav, amp)
    if wav2 is not None:
        wav2 = np.array(wav2)
        wav2 = to_16(wav2, amp)
        wav = np.stack([wav, wav2]).T
    
    wavfile.write(fname, SR, wav)