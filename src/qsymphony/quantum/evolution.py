# evolution.py
import numpy as np
from scipy.linalg import expm
from qiskit.circuit.library import PauliEvolutionGate
from qiskit.quantum_info import Statevector
from qiskit.synthesis import SuzukiTrotter

#first two are using two compare with the circuit evolution if needed

def evolve_exact(H, psi0, t):
    """Exact exp(-iHt)|psi0>, returned as a Statevector."""
    psi0 = Statevector(psi0)
    return Statevector(expm(-1j * t * H.to_matrix()) @ psi0.data)


def evolve_exact_trajectory(H, psi0, times):
    """
    Exact states at many times with ONE diagonalisation
    (much cheaper than calling expm per time step).
    """
    psi0 = Statevector(psi0)
    E, V = np.linalg.eigh(H.to_matrix())
    c = V.conj().T @ psi0.data
    return [Statevector(V @ (np.exp(-1j * E * t) * c)) for t in times]


def evolve_circuit(psi0_circuit, H, t, n_steps=20, order=2):
    """
    Circuit approximating exp(-iHt) via Suzuki-Trotter.
    Works for any SparsePauliOp (XX, YY, ZZ, X, Z ... terms), and takes H
    like evolve_exact does. order=2 has error O(t^3/n^2) vs O(t^2/n) for 1.
    """
    qc = psi0_circuit.copy()
    gate = PauliEvolutionGate(H, time=t,
                              synthesis=SuzukiTrotter(order=order, reps=n_steps))
    qc.append(gate, range(qc.num_qubits))
    return qc.decompose(reps=2)