from typing import Iterable


class WaveAdder:
    def __init__(self, *generators, stereo=False) -> None:
        self.generators = generators
        self.stereo = stereo

    def _mod_channels(self, _val):
        val = _val
        if isinstance(_val, (int, float)) and self.stereo:
            val = (_val, _val)
        elif isinstance(_val, Iterable) and not self.stereo:
            val = sum(_val) / len(_val)
        return val

    def trigger_release(self):
        [
            gen.trigger_release()
            for gen in self.generators
            if hasattr(gen, "trigger_release")
        ]

    @property
    def ended(self):
        ended = [gen.ended for gen in self.generators if hasattr(gen, "ended")]
        return all(ended)

    def __iter__(self):
        [iter(gen) for gen in self.generators]
        return self

    def __next__(self):
        vals = [self._mod_channels(next(gen)) for gen in self.generators]
        if self.stereo:
            l, r = zip(*vals)
            val = (sum(l) / len(l), sum(r) / len(r))
        else:
            val = sum(vals) / len(vals)
        return val


class Chain:
    def __init__(self, generator, *modifiers) -> None:
        self.generator = generator
        self.modifiers = modifiers

    def __getattr__(self, attr):
        val = None
        if hasattr(self.generator, attr):
            val = getattr(self.generator, attr)
        else:
            for modifier in self.modifiers:
                if hasattr(modifier, attr):
                    val = getattr(modifier, attr)
                    break
            else:
                raise AttributeError(f"attribute '{attr}' does not exist")
        return val

    def trigger_release(self):
        tr = "trigger_release"
        if hasattr(self.generator, tr):
            self.generator.trigger_release()
        for mod in self.modifiers:
            if hasattr(mod, tr):
                mod.trigger_release()

    def __iter__(self):
        iter(self.generator)
        [iter(mod) for mod in self.modifiers if hasattr(mod, "__iter__")]
        return self

    def __next__(self):
        val = next(self.generator)
        [next(mod) for mod in self.modifiers if hasattr(mod, "__next__")]
        for mod in self.modifiers:
            val = mod(val)
        return val
