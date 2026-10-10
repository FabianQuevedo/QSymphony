# hamiltonians.py
from qiskit.quantum_info import SparsePauliOp

def two_qubit_hamiltonian(J, h, *, Jyy=0.0, Jzz=0.0,
                          h0=None, h1=None, hx0=0.0, hx1=0.0):
    """
    H = J XX + Jyy YY + Jzz ZZ + h0 Z_0 + h1 Z_1 + hx0 X_0 + hx1 X_1

    default is H = J XX + h (Z_0 + Z_1).
    h0 / h1 default to h. Qiskit labels: rightmost character = qubit 0.
    """
    h0 = h if h0 is None else h0
    h1 = h if h1 is None else h1
    terms = [("XX", J), ("YY", Jyy), ("ZZ", Jzz),
             ("IZ", h0), ("ZI", h1), ("IX", hx0), ("XI", hx1)]
    return SparsePauliOp.from_list([(l, c) for l, c in terms if c != 0])