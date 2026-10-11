# states.py
from qiskit import QuantumCircuit
from qiskit.quantum_info import Statevector


def basis_state(bits="00"):
    qc = QuantumCircuit(len(bits))
    for q, bit in enumerate(reversed(bits)):
        if bit == "1":
            qc.x(q)
    return qc


def bell_state(kind="phi+"):
    """phi+ = (|00>+|11>)/sqrt2, psi+ = (|01>+|10>)/sqrt2."""
    qc = QuantumCircuit(2)
    if kind == "psi+":
        qc.x(1)
    qc.h(0)
    qc.cx(0, 1)
    return qc


def plus_state(n=2):
    """|+>^n: maximal coherence in the computational basis."""
    qc = QuantumCircuit(n)
    qc.h(range(n))
    return qc


def exact_initial_state(circuit):
    """Statevector of a preparation circuit."""
    return Statevector.from_instruction(circuit)
