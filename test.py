import sys
import subprocess

required_packages = {
    "numpy": "numpy",
    "scipy": "scipy",
    "qiskit": "qiskit",
    "qiskit_aer": "qiskit-aer",
    "mido": "mido",
    "matplotlib": "matplotlib"
}

for module, pip_name in required_packages.items():
    try:
        __import__(module)
    except ImportError:
        print(f"Module '{module}' not found. Installing '{pip_name}'...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

import os
import numpy as np
import mido
from mido import Message, MidiFile, MidiTrack, MetaMessage
from qiskit.quantum_info import Statevector, state_fidelity

base_path = os.getcwd()
paths = [
    os.path.abspath(os.path.join(base_path, "src")),
    os.path.abspath(os.path.join(base_path, "src", "qsymphony", "quantum")),
    os.path.abspath(os.path.join(base_path, "src", "qsymphony", "music")),
]
for p in paths:
    if p not in sys.path:
        sys.path.insert(0, p)

from qsymphony.quantum.states import basis_state, exact_initial_state, plus_state
from qsymphony.quantum.hamiltonians import two_qubit_hamiltonian
from qsymphony.quantum.evolution import evolve_exact, evolve_circuit, evolve_exact_trajectory
from qsymphony.quantum.observables import populations, pair_correlations, bloch_vectors, expectation, pauli_observable, snapshot
from qsymphony.quantum.measurements import measure_paulis

print("basis_state('01') ->", Statevector.from_instruction(basis_state("01")).probabilities_dict())
print("\n" + "-" * 40)

H0 = two_qubit_hamiltonian(1.0, 0.7)
psi = evolve_exact(H0, exact_initial_state(basis_state("00")), 1.3)
print("orig model pops:", {k: round(v, 3) for k, v in populations(psi).items()})
pc = pair_correlations(psi)[(0, 1)]
b = bloch_vectors(psi)
print("orig XX, YY:", round(pc["XX"], 3), round(pc["YY"], 3), "| Z0, Z1:", round(b[0, 2], 3), round(b[1, 2], 3))
print("\n" + "-" * 40)

H = two_qubit_hamiltonian(1.0, 0.7, Jyy=0.4, Jzz=0.3, h1=-0.5, hx0=0.6)
prep = plus_state(2)
t = 2.0
ex = evolve_exact(H, Statevector.from_instruction(prep), t)
for order, n in [(1, 20), (2, 20)]:
    qc = evolve_circuit(prep, H, t, n, order)
    print(f"trotter order {order}, n={n}: infidelity =", 1 - state_fidelity(Statevector.from_instruction(qc), ex))

traj = evolve_exact_trajectory(H, Statevector.from_instruction(prep), [0, t])
print("trajectory matches expm:", np.allclose(traj[1].data, ex.data))
print("\n" + "-" * 40)

qc = evolve_circuit(prep, H, t, 20, 2)
labels = ["XX", "YY", "ZZ", "IZ", "ZI", "IX", "XI"]
res, counts = measure_paulis(qc, labels, shots=50_000, seed=1)
print("settings used:", list(counts))
exact_state = Statevector.from_instruction(qc)
for l in labels:
    print(l, round(res[l][0], 3), "+-", round(res[l][1], 3), "exact", round(expectation(exact_state, pauli_observable(l)), 3))

s = snapshot(ex)
print("\nl1 coh:", round(s["coherence_l1"], 3), "| S(q0):", round(s["entropy_q0"], 3))

def export_to_midi(events, bpm, filename="qsymphony_output.mid"):
    mid = MidiFile()
    track = MidiTrack()
    mid.tracks.append(track)

    tempo = mido.bpm2tempo(int(bpm))
    track.append(MetaMessage('set_tempo', tempo=tempo, time=0))
    ticks_per_beat = mid.ticks_per_beat

    midi_events = []
    for ev in events:
        start_tick = int(ev.start * ticks_per_beat)
        end_tick = int((ev.start + ev.dur) * ticks_per_beat)
        channel = 0 if ev.voice == "melody" else 1

        midi_events.append({'type': 'note_on', 'time': start_tick, 'note': ev.pitch, 'velocity': ev.velocity, 'channel': channel})
        midi_events.append({'type': 'note_off', 'time': end_tick, 'note': ev.pitch, 'velocity': 0, 'channel': channel})

    midi_events.sort(key=lambda x: x['time'])

    last_time = 0
    for me in midi_events:
        delta = me['time'] - last_time
        track.append(Message(me['type'], note=me['note'], velocity=me['velocity'], time=delta, channel=me['channel']))
        last_time = me['time']

    mid.save(filename)
    print(f"MIDI file generated successfully: {filename}")

from qsymphony.music.composer import compose
from qsymphony.music.params import HamParams, MusicStyle

sections = [
    (HamParams(J=1.0, h=0.7), 16),
    (HamParams(J=2.0, h=0.1, Jzz=1.5), 32),
    (HamParams(J=0.5, h=2.0, hx0=1.0, hx1=1.0), 16)
]

prep_circuit = plus_state(2)

print("Simulating quantum trajectory and composing...")
musical_events, _, base_style = compose(
    sections=sections,
    prep=prep_circuit,
    mode="exact",
    seed=42
)

export_to_midi(musical_events, bpm=base_style.bpm, filename="Quantum_Playground_Track.mid")
