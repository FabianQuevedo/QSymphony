# observables.py
import itertools
import numpy as np
from qiskit.quantum_info import (Statevector, DensityMatrix, SparsePauliOp,
                                 partial_trace, entropy)


def _sv(psi):
    return psi if isinstance(psi, Statevector) else Statevector(psi)


def pauli_observable(pauli_string):
    """Qiskit order, e.g. 'ZI' = Z on qubit 1. Rightmost char = qubit 0."""
    return SparsePauliOp(pauli_string)


def pauli_on(n, ops):
    """pauli_on(2, {0: 'Z'}) -> 'IZ'. Avoids hand-written label order."""
    s = ["I"] * n
    for q, p in ops.items():
        s[n - 1 - q] = p
    return SparsePauliOp("".join(s))


def expectation(psi, observable):
    return float(np.real(_sv(psi).expectation_value(observable)))


# ---------- populations (diagonal of rho) ----------
def populations(psi):
    """{'00': p, '01': p, ...} in Qiskit label order, zeros included."""
    sv = _sv(psi)
    n = sv.num_qubits
    return {format(i, f"0{n}b"): float(p) for i, p in enumerate(sv.probabilities())}


def population(psi, label):
    return populations(psi)[label]


# ---------- coherences (off-diagonal of rho, computational basis) ----------
def coherence_matrix(psi):
    """|rho_ij| for i != j (0 on the diagonal). Basis dependent."""
    rho = DensityMatrix(_sv(psi)).data
    return np.abs(rho - np.diag(np.diag(rho)))


def l1_coherence(psi):
    """l1-norm of coherence: sum of |rho_ij|, i != j."""
    return float(coherence_matrix(psi).sum())


# ---------- single-qubit and pair features ----------
def bloch_vectors(psi):
    """Array (n, 3) of <X>,<Y>,<Z> for each qubit. Length < 1 => entangled."""
    n = _sv(psi).num_qubits
    return np.array([[expectation(psi, pauli_on(n, {q: p})) for p in "XYZ"]
                     for q in range(n)])


def pair_correlations(psi):
    """
    {(i, j): {'XX':..,'YY':..,'ZZ':.., 'XX_c':.., ...}}
    '_c' = connected correlation <AB> - <A><B> (purely quantum/classical
    correlation, with the local-field part removed).
    """
    n = _sv(psi).num_qubits
    out = {}
    for i, j in itertools.combinations(range(n), 2):
        d = {}
        for p in "XYZ":
            ab = expectation(psi, pauli_on(n, {i: p, j: p}))
            a = expectation(psi, pauli_on(n, {i: p}))
            b = expectation(psi, pauli_on(n, {j: p}))
            d[p + p] = ab
            d[p + p + "_c"] = ab - a * b
        out[(i, j)] = d
    return out


def entanglement_entropy(psi, qubit=0):
    """Von Neumann entropy (bits) of one qubit vs the rest."""
    sv = _sv(psi)
    others = [q for q in range(sv.num_qubits) if q != qubit]
    return float(entropy(partial_trace(DensityMatrix(sv), others)))


def snapshot(psi):
    """Everything phase 2 (the music mapping) needs from one quantum state."""
    return {
        "populations": populations(psi),
        "coherence_l1": l1_coherence(psi),
        "coherence_matrix": coherence_matrix(psi),
        "bloch": bloch_vectors(psi),
        "pair_correlations": pair_correlations(psi),
        "entropy_q0": entanglement_entropy(psi, 0),
    }