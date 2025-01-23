This is a small library that implements Qiskit's [TwoLocal](https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.TwoLocal) and [ZZFeatureMap](https://docs.quantum.ibm.com/api/qiskit/qiskit.circuit.library.ZZFeatureMap) circuits into Pennylane.

Example usage:
```python
import pennylane as qml
import circuit_lib as cl
import numpy as np

dev = qml.device(device = "default.qubit", wires = 4)

ZZFeatureMap = cl.create_ZZFeatureMap(dev)
TwoLocal = cl.create_TwoLocal(dev, num_rep = 2, entanglement_type = cl.SCA)

data = np.ones(shape = (4,))
# Params must be in shape (number of repitions + 1, number of wires))
params = np.random.default_rng().random(size = (3, 4))

@qml.qnode(dev)
def quantum_circuit(params, x):
  ZZFeatureMap(x)
  TwoLocal(params)
  return qml.State()

print(quantum_circuit(params, data)) #Big endian ordering
```
