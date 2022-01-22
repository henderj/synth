import math
from abc import ABC, abstractmethod


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

    @frequency.setter
    def frequency(self, value):
        self._f = value
        self._post_frequency_set()

    @property
    def amplitude(self):
        return self._a

    @amplitude.setter
    def amplitude(self, value):
        self._a = value
        self._post_amplitude_set()

    @property
    def phase(self):
        return self._p

    @phase.setter
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
        self._p = (self._p / 360) * 2 * math.pi

    def _initialize_oscillator(self):
        self._i = 0

    def __next__(self):
        val = math.sin(self._i + self._p)
        self._i = self._i + self._step
        if self._wave_range != (-1, 1):
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
        if self._wave_range != (-1, 1):
            val = self.squish_value(val, *self._wave_range)
        return val * self._a


class TriangleOscillator(SawtoothOscillator):
    def __next__(self):
        div = (self._i + self._p) / self._period
        val = 2 * (div - math.floor(0.5 + div))
        val = (abs(val) - 0.5) * 2
        self._i = self._i + 1
        if self._wave_range != (-1, 1):
            val = self.squish_val(val, *self._wave_range)
        return val * self._a


class ModulatedOscillator:
    def __init__(
        self, oscillator, *modulators, amp_mod=None, freq_mod=None, phase_mod=None
    ) -> None:
        self.oscillator = oscillator
        self.modulators = modulators
        self.amp_mod = amp_mod
        self.freq_mod = freq_mod
        self.phase_mod = phase_mod
        self._modulators_count = len(modulators)

    def __iter__(self):
        iter(self.oscillator)
        [iter(modulator) for modulator in self.modulators]
        return self

    def _modulate(self, mod_vals):
        if self.amp_mod is not None:
            new_amp = self.amp_mod(self.oscillator.init_amp, mod_vals[0])
            self.oscillator.amp = new_amp

        if self.freq_mod is not None:
            if self._modulators_count == 2:
                mod_val = mod_vals[1]
            else:
                mod_val = mod_vals[0]
            new_freq = self.freq_mod(self.oscillator.init_freq, mod_val)
            self.oscillator.freq = new_freq

        if self.phase_mod is not None:
            if self._modulators_count == 3:
                mod_val = mod_vals[2]
            else:
                mod_val = mod_vals[-1]
            new_phase = self.phase_mod(self.oscillator.init_phase, mod_val)
            self.oscillator.phase = new_phase

    def trigger_release(self):
        tr = "trigger_release"
        for modulator in self.modulators:
            if hasattr(modulator, tr):
                modulator.trigger_release()
        if hasattr(self.oscillator, tr):
            self.oscillator.trigger_release()

    @property
    def ended(self):
        e = "ended"
        ended = []
        for modulator in self.modulators:
            if hasattr(modulator, e):
                ended.append(modulator.ended)
        if hasattr(self.oscillator, e):
            ended.append(self.oscillator.ended)
        return all(ended)

    def __next__(self):
        mod_vals = [next(modulator) for modulator in self.modulators]
        self._modulate(mod_vals)
        return next(self.oscillator)
