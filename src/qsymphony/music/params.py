# params.py  -- Hamiltonian parameters and the (separate) musical style
from dataclasses import dataclass
from typing import Optional, Tuple
import numpy as np
from hamiltonians import two_qubit_hamiltonian


@dataclass(frozen=True)
class HamParams:
    """The 'composer knobs'. Each set of values = one musical character."""
    J: float = 1.0                 # XX coupling
    h: float = 0.7                 # default Z field on both qubits
    Jyy: float = 0.0
    Jzz: float = 0.0
    h0: Optional[float] = None     # Z field on qubit 0 (defaults to h)
    h1: Optional[float] = None     # Z field on qubit 1 (defaults to h)
    hx0: float = 0.0               # X field on qubit 0
    hx1: float = 0.0

    def build(self):
        return two_qubit_hamiltonian(self.J, self.h, Jyy=self.Jyy, Jzz=self.Jzz,
                                     h0=self.h0, h1=self.h1,
                                     hx0=self.hx0, hx1=self.hx1)


@dataclass
class MusicStyle:
    """Musical conventions. Independent of the physics; override freely."""
    root: int = 60                         # MIDI note of the tonic (C4)
    mode: str = "minor"                    # key in music_theory.SCALES
    bpm: float = 100.0
    beats_per_frame: float = 1.0           # one quantum snapshot = one beat
    melody_offsets: Tuple[int, ...] = (0, 2, 4, 7)   # basis state k -> scale degree


def style_from_hamiltonian(p: HamParams) -> MusicStyle:
    """
    Optional H -> style link (design choices, tune them):
      sign(Jzz) -> mode : >0 (antiferro, frustrated) minor, <0 (ferro) major, 0 dorian
      energy scale -> tempo
    """
    mode = "minor" if p.Jzz > 0 else "major" if p.Jzz < 0 else "dorian"
    scale = float(np.linalg.norm(p.build().coeffs))
    return MusicStyle(mode=mode, bpm=round(70 + 50 * np.tanh(scale / 2)))


def auto_dt(H, steps_per_period=16):
    """
    Time step per beat taken from the spectrum: the *typical* Bohr period
    (median of |Ei - Ej|) is spread over `steps_per_period` beats, so the
    physics always oscillates at a musically useful rate whatever J, h are.
    """
    E = np.linalg.eigvalsh(H.to_matrix())
    d = np.abs(E[:, None] - E[None, :])[np.triu_indices(len(E), 1)]
    d = d[d > 1e-9]
    return float(2 * np.pi / np.median(d) / steps_per_period)
