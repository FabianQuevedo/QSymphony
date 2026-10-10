## Provisional instructions

In src/quantum is now the part that generates the circuit, there are 5 files so far

states.py
Builds the initial preparation circuits: computational basis states, Bell states and |+>ⁿ.

hamiltonian.py
two_qubit_hamiltonian returns a SparsePauliOp with XX, YY and ZZ couplings plus per-qubit Z and X fields. Its defaults reproduce your original J XX + h(Z0+Z1), and the extra terms break the symmetry that froze the dynamics.

evolution.py
evolve_exact and evolve_exact_trajectory give exact time evolution, the latter for many times with one diagonalisation. evolve_circuit builds a second-order Trotter circuit for hardware or noisy simulation.

observables.py
Extracts the quantities that are going to fed the musical materiall from a statevector: populations, coherences, Bloch vectors, pair correlations and entanglement entropy.
snapshot(psi) bundles all of these into one dict for the music-mapping phase.

measurements.py
Estimates Pauli expectations from sampled shots, with an optional noise model and seed.
measure_paulis groups compatible strings so XX, YY, ZZ and the single-qubit terms need only 3 circuits.

#what's still missing (pu to this commit), the music mapping. A check of the modules already constructed is on a notebook (ins only checking all seems to work fine)
