from typing import Iterable


class Volume:
    def __init__(self, amp=1.0) -> None:
        self.amp = amp

    def __call__(self, val):
        _val = None
        if isinstance(val, Iterable):
            _val = tuple(v * self.amp for v in val)
        elif isinstance(val, (int, float)):
            _val = val * self.amp
        return _val


class ModulatedVolume(Volume):
    def __init__(self, modulator) -> None:
        super().__init__(0.0)
        self.modulator = modulator

    def __iter__(self):
        iter(self.modulator)
        return self

    def __next__(self):
        self.amp = next(self.modulator)
        return self.amp

    def trigger_release(self):
        if hasattr(self.modulator, "trigger_release"):
            self.modulator.trigger_release()

    @property
    def ended(self):
        ended = False
        if hasattr(self.modulator, "ended"):
            ended = self.modulator.ended
        return ended


class Panner:
    def __init__(self, r) -> None:
        self.r = r

    def __call__(self, val):
        r = self.r * 2
        l = 2 - r
        return (l * val, r * val)


class ModulatedPanner(Panner):
    def __init__(self, modulator) -> None:
        super().__init__(r=0)
        self.modulator = modulator

    def __iter__(self):
        iter(self.modulator)
        return self

    def __next__(self):
        self.r = (next(self.modulator) + 1) / 2
        return self.r
