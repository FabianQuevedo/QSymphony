QSymphony

Quantum dynamics → music. QSymphony simulates a small interacting quantum system (two qubits) with Qiskit and turns what the quantum state is doing into a piece of music: populations become the melody, coherences drive the rhythmic motion, and correlations and entanglement shape the harmony.

The physics is the composer. You choose Hamiltonian parameters (couplings and fields); the way the state evolves in time decides which notes, chords and rhythms are played.

How it works
 Hamiltonian parameters ──► quantum evolution ──► observables ──► musical mapping ──► MIDI / WAV
   (HamParams, sections)     exact or Trotter      per beat         melody, motion,
                             circuit               snapshot         harmony
Prepare a state (basis_state, bell_state, plus_state).
Build a Hamiltonian H = J XX + Jyy YY + Jzz ZZ + h0 Z0 + h1 Z1 + hx0 X0 + hx1 X1 (default J XX + h (Z0 + Z1); the extra terms break the symmetry that otherwise confines the dynamics to {|00>, |11>}).
Evolve it, either exactly (evolve_exact, evolve_exact_trajectory) or as a second-order Trotter circuit (evolve_circuit) for noisy / shot-based runs.
Extract features at every time step: populations, coherences, Bloch vectors, pair correlations (raw and connected) and entanglement entropy (snapshot). These can be computed exactly from the statevector or estimated from sampled measurements (measure_paulis needs only 3 measurement settings for XX, YY, ZZ and the single-qubit terms).
Map to music and export a MIDI file, which can then be rendered to audio.
Musical mapping
Quantum quantity	Musical role	How
Populations of |00>,|01>,|10>,|11>	Melody	Each note is a Born-rule sample of the populations; basis state k selects a scale degree above the current chord root. More probable notes are louder.
Coherence (single-qubit l1 coherence, sqrt(<X>²+<Y>²))	Motion	Sets notes per beat (1, 2 or 4) and legato. Basis-state-like states are sparse and staccato; superpositions flow.
<Z0 Z1>	Harmony: chord root	Aligned qubits give the tonic; anti-aligned qubits give more tense scale degrees.
Entanglement entropy	Harmony: chord size	Dyad → triad → 7th → 9th as entanglement grows.
abs(XX_c) + abs(YY_c)	Harmony: colour	Large transverse correlations replace the third with a suspended fourth.

Chords are stacked inside the chosen scale, so harmony never clashes with the key. All of these are design choices, meant to be tuned.

Hamiltonian parameters as compositional knobs
A section is a pair (HamParams, n_frames). The quantum state is carried across sections, so changing the parameters between sections is a quench, which acts as a musical section change.
auto_dt derives the time step per beat from the Hamiltonian's typical energy gap, so the dynamics oscillate at a musical rate whatever the couplings.
style_from_hamiltonian optionally links physics to style: the sign of Jzz selects the mode (minor / major / dorian) and the energy scale sets the tempo. Key, mode, tempo and register can also be set directly with MusicStyle.
Project layout
QSymphony/
├── src/qsymphony/
│   ├── quantum/        # states, hamiltonians, evolution, observables, measurements
│   └── music/          # params, composer and the feature/note mapping
├── configs/            # configuration files
├── test.py             # end-to-end check of the quantum modules + composes a MIDI track
├── render_audio.py     # MIDI → WAV with a small built-in synthesiser
├── generate_visuals.py # plots entropy and populations over time (quantum_dynamics.png)
├── Quantum_Playground_Track.mid   # example output
├── quantum_audio.wav              # example rendered audio
├── quantum_dynamics.png           # example plot
└── requirements.txt
quantum/
Module	Purpose
states.py	Preparation circuits: computational basis states, the four Bell states, |+>^n. Bitstrings follow Qiskit's order (rightmost character = qubit 0).
hamiltonians.py	two_qubit_hamiltonian(...) returns a SparsePauliOp.
evolution.py	Exact evolution (single time or a whole trajectory with one diagonalisation) and a Trotter circuit builder.
observables.py	Populations, coherence matrix and l1 coherence, Bloch vectors, pair correlations, entanglement entropy and snapshot(psi).
measurements.py	Shot-based Pauli estimation with optional noise model and seed.

Usage

Run the full pipeline (module checks, quantum evolution, composition, MIDI export):

bash
python test.py          # writes Quantum_Playground_Track.mid
python render_audio.py  # renders it to quantum_audio.wav
python generate_visuals.py  # writes quantum_dynamics.png

Compose your own piece:

python
from qsymphony.quantum.states import plus_state
from qsymphony.music.params import HamParams
from qsymphony.music.composer import compose

sections = [
    (HamParams(J=1.0, h=0.7), 16),                 # calm opening
    (HamParams(J=2.0, h=0.1, Jzz=1.5), 32),        # strongly coupled middle
    (HamParams(J=0.5, h=2.0, hx0=1.0, hx1=1.0), 16),
]
events, features, style = compose(sections, plus_state(2), mode="exact", seed=42)

mode="circuit" runs a Trotter circuit and estimates the features from shots instead (slower; it builds one circuit and one batch of shots per beat). The seed makes the Born-rule note sampling reproducible.

