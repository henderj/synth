from librosa import note_to_hz as hz
from pygame import MIDIIN

from composers import Chain
from modifiers import ModulatedPanner
from oscillators import SineOscillator, TriangleOscillator
from utils import get_samples, gettrig, wave_to_file


def main():
    MIDIIN.init()
    default_id = MIDIIN.get_default_input_id()
    midi_input = MIDIIN.Input(device_id=default_id)

    stream = pyaudio.PyAudio().open(
        rate=44100,
        channels=1,
        format=pyaudio.paInt16,
        output=True,
        frames_per_buffer=256,
    )

    try:
        notes_dict = {}
        while True:
            if notes_dict:
                # Play the notes
                samples = get_samples(notes_dict)
                samples = np.int16(samples).tobytes()
                stream.write(samples)

            if midi_input.poll():
                # Add or remove notes from notes_dict
                for event in midi_input.read(num_events=16):
                    (status, note, vel, _), _ = event
                    if status == 0x80 and note in notes_dict:
                        del notes_dict[note]
                    elif status == 0x90 and note not in notes_dict:
                        freq = midi.midi_to_frequency(note)
                        notes_dict[note] = get_sin_oscillator(freq=freq, amp=vel / 127)

    except KeyboardInterrupt as err:
        print("Stopping...")


# osc = SineOscillator()
# wav = get_seq(osc)
# wave_to_file(wav, fname="c4_maj_sine.wav")

# gen = Chain(
#     SineOscillator(220), ModulatedPanner(SineOscillator(4, wave_range=(-0.8, 0.8)))
# )
# wav = gettrig(gen, 4)
# wave_to_file(wav, fname="idk.wav")

if __name__ == "__main__":
    main()
