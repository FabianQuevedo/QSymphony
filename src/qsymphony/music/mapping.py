# mapping.py -- THE creative core: quantum features -> musical events
#   populations  -> melody   (which note)
#   coherence    -> motion   (rhythmic density, articulation)
#   correlations -> harmony  (chord root, size, colour)
from dataclasses import dataclass
import numpy as np
from music_theory import scale_pitch, fold


@dataclass
class NoteEvent:
    pitch: int
    start: float      # in beats
    dur: float        # in beats
    velocity: int
    voice: str        # "melody" | "harmony"


# scale degrees ordered from most stable (I) to most tense (vii°)
TENSION_LADDER = [0, 3, 4, 5, 1, 2, 6]


def harmony_from_features(f):
    """
    <Z0Z1> -> chord root: aligned qubits (+1) = tonic (rest), anti-aligned
               (-1) = tense degree. Harmony drifts as correlations build.
    entropy -> chord size: dyad / triad / 7th / 9th as entanglement grows.
    |XX_c|+|YY_c| -> 'sus' colour (3rd replaced by 4th) when large.
    Chords are stacked in thirds *inside the scale*, so they never clash with the key.
    """
    tension = (1 - np.clip(f.zz, -1, 1)) / 2
    root_deg = TENSION_LADDER[int(round(tension * 6))]
    if f.entropy < 0.15:
        stack = [0, 4]
    elif f.entropy < 0.5:
        stack = [0, 2, 4]
    elif f.entropy < 0.8:
        stack = [0, 2, 4, 6]
    else:
        stack = [0, 2, 4, 6, 8]
    if min(1.0, abs(f.xx_c) + abs(f.yy_c)) > 0.4:
        stack = [3 if s == 2 else s for s in stack]
    return root_deg, stack


def motion_from_features(f):
    """
    coherence -> notes per beat (1, 2 or 4) and legato (0.4..0.95).
    Basis-state-like (no coherence) = sparse & staccato; superposition = flowing.
    """
    c = f.coherence
    sub = 1 if c < 1 / 3 else 2 if c < 2 / 3 else 4
    return sub, 0.4 + 0.55 * c


def frame_to_events(f, style, beat0, rng, sample=True):
    root_deg, stack = harmony_from_features(f)
    sub, legato = motion_from_features(f)
    n = style.beats_per_frame
    events = []

    # harmony: sustained chord, low register
    lo = style.root - 12
    chord = {fold(scale_pitch(style.root, style.mode, root_deg + s) - 12, lo, lo + 16)
             for s in stack}
    events += [NoteEvent(p, beat0, n * 0.98, 55, "harmony") for p in sorted(chord)]

    # melody: each note is a Born-rule sample of the populations
    pops = np.asarray(f.pops) / np.sum(f.pops)
    for i in range(sub):
        k = int(rng.choice(len(pops), p=pops)) if sample else int(np.argmax(pops))
        p = scale_pitch(style.root, style.mode, root_deg + style.melody_offsets[k]) + 12
        p = fold(p, style.root + 4, style.root + 23)
        vel = int(np.clip(45 + 70 * pops[k], 1, 127))   # likelier note = louder
        events.append(NoteEvent(p, beat0 + i * n / sub, n / sub * legato, vel, "melody"))
    return events
