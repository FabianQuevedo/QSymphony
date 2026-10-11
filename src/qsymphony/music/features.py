# features.py -- one quantum state -> the numbers the music mapping uses
from dataclasses import dataclass
import numpy as np
from observables import (populations, bloch_vectors, pair_correlations,
                         entanglement_entropy)
from measurements import measure_paulis


@dataclass
class Features:
    pops: np.ndarray    # length 4, index = int(label,2): bit0 = qubit 0
    coherence: float    # mean single-qubit l1 coherence sqrt(<X>^2+<Y>^2), in [0,1]
    zz: float           # <Z0 Z1>
    zz_c: float         # connected correlations <AB>-<A><B>
    xx_c: float
    yy_c: float
    entropy: float      # entanglement entropy of qubit 0 (bits), in [0,1]


def _coherence(b):
    return float(np.mean(np.hypot(b[:, 0], b[:, 1])))


def _h2(r):
    """Binary entropy of a qubit with Bloch length r (entanglement proxy)."""
    p = np.clip((1 + r) / 2, 1e-12, 1 - 1e-12)
    return float(-(p * np.log2(p) + (1 - p) * np.log2(1 - p)))


def features_from_state(psi):
    """Exact path (statevector)."""
    pops = np.array(list(populations(psi).values()))
    pc = pair_correlations(psi)[(0, 1)]
    return Features(pops, _coherence(bloch_vectors(psi)), pc["ZZ"], pc["ZZ_c"],
                    pc["XX_c"], pc["YY_c"], entanglement_entropy(psi, 0))


_PAULIS = ["IZ", "ZI", "IX", "XI", "IY", "YI", "XX", "YY", "ZZ"]


def features_from_circuit(qc, shots=4000, seed=None, backend=None, noise_model=None):
    """Shot-based path: same features, estimated from 3 measurement settings."""
    res, counts = measure_paulis(qc, _PAULIS, shots, backend, noise_model, seed)
    e = lambda p: res[p][0]
    b = np.array([[e("IX"), e("IY"), e("IZ")],      # qubit 0
                  [e("XI"), e("YI"), e("ZI")]])     # qubit 1
    cz = counts["ZZ"]
    tot = sum(cz.values())
    pops = np.zeros(4)
    for bits, c in cz.items():
        pops[int(bits.replace(" ", ""), 2)] += c / tot
    return Features(pops, _coherence(b), e("ZZ"), e("ZZ") - b[0, 2] * b[1, 2],
                    e("XX") - b[0, 0] * b[1, 0], e("YY") - b[0, 1] * b[1, 1],
                    _h2(np.linalg.norm(b[0])))
