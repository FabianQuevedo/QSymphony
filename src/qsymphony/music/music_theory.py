# music_theory.py
SCALES = {
    "major":  [0, 2, 4, 5, 7, 9, 11],
    "minor":  [0, 2, 3, 5, 7, 8, 10],
    "dorian": [0, 2, 3, 5, 7, 9, 10],
    "pentatonic": [0, 2, 4, 7, 9],
}


def scale_pitch(root, mode, degree):
    """MIDI pitch of any (possibly negative / >octave) scale degree."""
    s = SCALES[mode]
    octave, idx = divmod(degree, len(s))
    return root + 12 * octave + s[idx]


def fold(p, lo, hi):
    """Shift by octaves into [lo, hi] (window must be >= 12 wide)."""
    while p > hi:
        p -= 12
    while p < lo:
        p += 12
    return p
