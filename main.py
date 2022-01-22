from librosa import note_to_hz as hz

from composers import Chain
from modifiers import ModulatedPanner
from oscillators import SineOscillator, TriangleOscillator
from utils import gettrig, wave_to_file


# osc = SineOscillator()
# wav = get_seq(osc)
# wave_to_file(wav, fname="c4_maj_sine.wav")

gen = Chain(
    SineOscillator(220), ModulatedPanner(SineOscillator(4, wave_range=(-0.8, 0.8)))
)
wav = gettrig(gen, 4)
wave_to_file(wav, fname="idk.wav")
