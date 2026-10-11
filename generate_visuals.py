import sys
import os

base_path = os.getcwd()
paths = [
    os.path.abspath(os.path.join(base_path, "src")),
    os.path.abspath(os.path.join(base_path, "src", "qsymphony", "quantum")),
    os.path.abspath(os.path.join(base_path, "src", "qsymphony", "music")),
]
for p in paths:
    if p not in sys.path:
        sys.path.insert(0, p)

import numpy as np
import matplotlib.pyplot as plt
from qiskit.quantum_info import Statevector

from qsymphony.quantum.states import plus_state
from qsymphony.quantum.hamiltonians import two_qubit_hamiltonian
from qsymphony.quantum.evolution import evolve_exact_trajectory
from qsymphony.quantum.observables import snapshot
from qsymphony.music.params import HamParams

sections = [
    (HamParams(J=1.0, h=0.7), 16),
    (HamParams(J=2.0, h=0.1, Jzz=1.5), 32),
    (HamParams(J=0.5, h=2.0, hx0=1.0, hx1=1.0), 16)
]

psi = Statevector.from_instruction(plus_state(2))

total_times = []
entropies = []
populations_00 = []
populations_11 = []

current_time = 0.0
dt = 0.1

print("Computing quantum trajectory for visualization...")
for params, n_frames in sections:
    H = params.build()
    t_sec = np.arange(n_frames) * dt
    states = evolve_exact_trajectory(H, psi, t_sec)

    for state in states:
        snap = snapshot(state)
        entropies.append(snap['entropy_q0'])
        populations_00.append(snap['populations']['00'])
        populations_11.append(snap['populations']['11'])
        total_times.append(current_time)
        current_time += dt

    psi = states[-1]

plt.style.use('dark_background')
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True)

ax1.plot(total_times, entropies, color='cyan', lw=2)
ax1.set_ylabel(r'Entropy $S(q_0)$')
ax1.set_title('Quantum Dynamics: Entanglement and Populations (QSymphony)')
ax1.axvline(x=16 * dt, color='gray', linestyle='--', alpha=0.6, label='Quench 1')
ax1.axvline(x=(16 + 32) * dt, color='gray', linestyle=':', alpha=0.6, label='Quench 2')
ax1.legend(loc='upper right')

ax2.plot(total_times, populations_00, color='magenta', label=r'$|00\rangle$', lw=2)
ax2.plot(total_times, populations_11, color='yellow', label=r'$|11\rangle$', lw=2)
ax2.set_ylabel('Probability')
ax2.set_xlabel('Simulation Time (a.u.)')
ax2.legend(loc='upper right')
ax2.axvline(x=16 * dt, color='gray', linestyle='--', alpha=0.6)
ax2.axvline(x=(16 + 32) * dt, color='gray', linestyle=':', alpha=0.6)

plt.tight_layout()
plt.savefig('quantum_dynamics.png', dpi=300)
print("Plot saved successfully as quantum_dynamics.png!")