# composer.py -- physics + mapping -> a full piece
import math
from dataclasses import replace
import numpy as np
from qiskit.quantum_info import Statevector
from evolution import evolve_exact, evolve_exact_trajectory, evolve_circuit
from features import features_from_state, features_from_circuit
from mapping import frame_to_events
from params import style_from_hamiltonian, auto_dt


def compose(sections, prep, *, mode="exact", shots=4000, seed=0,
            style=None, sample=True, trotter_dt=0.1):
    """
    sections: [(HamParams, n_frames), ...]. The quantum state is carried
    across sections, so changing the Hamiltonian parameters between sections
    is a 'quench' = a musical section change (A -> B).
    mode: "exact" (statevector) or "circuit" (Trotter circuit + shots).
    Returns (events, features_per_frame, first_style).
    """
    rng = np.random.default_rng(seed)
    psi = Statevector.from_instruction(prep)
    base_qc = prep
    beat, events, all_feats, first = 0.0, [], [], None

    for ham, nf in sections:
        H = ham.build()
        dt = auto_dt(H)
        sty = style or style_from_hamiltonian(ham)
        if first is None:
            first = sty
        else:
            sty = replace(sty, bpm=first.bpm)      # one tempo, per-section mode
        times = dt * np.arange(nf)

        if mode == "exact":
            feats = [features_from_state(s) for s in evolve_exact_trajectory(H, psi, times)]
            psi = evolve_exact(H, psi, nf * dt)
        else:
            feats = []
            for k, t in enumerate(times):
                qc = evolve_circuit(base_qc, H, t, max(1, math.ceil(t / trotter_dt)))
                feats.append(features_from_circuit(qc, shots, seed=seed + len(all_feats) + k))
            T = nf * dt
            base_qc = evolve_circuit(base_qc, H, T, max(1, math.ceil(T / trotter_dt)))

        for f in feats:
            events += frame_to_events(f, sty, beat, rng, sample)
            beat += sty.beats_per_frame
        all_feats += feats
    return events, all_feats, first
