from oscillators import SineOscillator
from utils import get_seq, wave_to_file


class WaveAdder:
    def __init__(self, *oscillators) -> None:
        self.oscillators = oscillators
        self.n = len(oscillators)

    def __iter__(self):
        [iter(osc) for osc in self.oscillators]
        return self

    def __next__(self):
        return sum(next(osc) for osc in self.oscillators) / self.n


osc = SineOscillator()
wav = get_seq(osc)
wave_to_file(wav, fname="c4_maj_sine.wav")
