# measurements.py
import numpy as np
from qiskit import transpile
from qiskit_aer import AerSimulator


def _validate(circuit, paulis):
    n = circuit.num_qubits
    for p in paulis:
        if len(p) != n:
            raise ValueError(f"Pauli string {p!r} must have length {n}.")
        if set(p) - set("IXYZ"):
            raise ValueError(f"Unsupported Pauli in {p!r}.")


def _group_paulis(paulis):
    """Greedy qubit-wise-commuting grouping -> [(basis_string, [paulis])]."""
    groups = []
    for p in paulis:
        for g in groups:
            if all(a == b or a == "I" or b == "I" for a, b in zip(g[0], p)):
                g[0] = "".join(a if a != "I" else b for a, b in zip(g[0], p))
                g[1].append(p)
                break
        else:
            groups.append([p, [p]])
    return [(b, m) for b, m in groups]


def _measurement_circuit(circuit, basis):
    n = circuit.num_qubits
    qc = circuit.copy()
    qc.barrier()
    for q in range(n):
        p = basis[n - 1 - q]          # rightmost char = qubit 0
        if p == "X":
            qc.h(q)
        elif p == "Y":
            qc.sdg(q)
            qc.h(q)
    qc.measure_all()
    return qc


def _estimate(counts, pauli):
    # Bitstring and Pauli string share Qiskit's order (rightmost = qubit 0),
    # so characters line up index by index.
    total = sum(counts.values())
    acc = 0
    for bits, c in counts.items():
        bits = bits.replace(" ", "")
        parity = sum(int(b) for b, p in zip(bits, pauli) if p != "I") % 2
        acc += c * (-1) ** parity
    est = acc / total
    se = np.sqrt(max(0.0, 1 - est**2) / total)
    return est, se


def measure_paulis(circuit, pauli_strings, shots=10_000, backend=None,
                   noise_model=None, seed=None):
    """
    Estimate many Pauli strings at once. Strings that are qubit-wise
    compatible share one measurement setting, so XX, YY, ZZ, ZI, IZ ...
    need only 3 circuits (X, Y and Z bases) instead of one each.
    Returns ({pauli: (estimate, std_error)}, {basis: counts}).
    """
    pauli_strings = list(dict.fromkeys(pauli_strings))
    _validate(circuit, pauli_strings)
    if backend is None:
        backend = AerSimulator(noise_model=noise_model)
    elif noise_model is not None:
        raise ValueError("Pass noise_model only when backend is None.")

    kwargs = {} if seed is None else {"seed_simulator": seed}
    results, all_counts = {}, {}
    for basis, members in _group_paulis(pauli_strings):
        compiled = transpile(_measurement_circuit(circuit, basis), backend)
        counts = backend.run(compiled, shots=shots, **kwargs).result().get_counts()
        all_counts[basis] = counts
        for p in members:
            results[p] = _estimate(counts, p)
    return results, all_counts


def measure_pauli(circuit, pauli_string, shots=10_000, backend=None,
                  noise_model=None, seed=None):
    """Single-Pauli convenience wrapper: (estimate, std_error, counts)."""
    res, counts = measure_paulis(circuit, [pauli_string], shots, backend,
                                 noise_model, seed)
    est, se = res[pauli_string]
    return est, se, counts[next(iter(counts))]