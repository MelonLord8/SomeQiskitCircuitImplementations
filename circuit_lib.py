import pennylane as qml

FULL = "full"
LINEAR = "linear"
REVERSE_LINEAR = "rev_linear"
PAIRWISE = "pairwise"
CIRCULAR = "circular"
SCA = "sca"

def create_two_local(device, num_rep = 1, entanglement_type = LINEAR):
    wires = device.wires
    num_wires = len(wires)

    def entanglement_layer():
        if entanglement_type == FULL:
            for i in range(num_wires - 1):
                for j in range(i + 1, num_wires):
                    qml.CNOT(wires = [wires[i], wires[j]])

        elif entanglement_type == LINEAR:
            for i in range(num_wires - 1):
                qml.CNOT(wires = [wires[i], wires[i+1]])

        elif entanglement_type == REVERSE_LINEAR:
            for i in range(num_wires - 2, -1, -1):
                qml.CNOT(wires = [wires[i], wires[i+1]])

        elif entanglement_type == PAIRWISE:
            for i in range(0, num_wires - 1, 2):
                qml.CNOT(wires = [wires[i], wires[i+1]])
            for i in range(1, num_wires - 1, 2):
                qml.CNOT(wires = [wires[i], wires[i+1]])

        elif entanglement_type == CIRCULAR:
            qml.CNOT(wires = [wires[num_wires - 1], wires[0]])
            for i in range(num_wires - 1):
                qml.CNOT(wires = [wires[i], wires[i+1]])

    def sca_entanglement_layer(layer):
        for wire_id in range(num_wires - layer, 2*num_wires - layer ):
            if layer % 2 == 1:
                control = wires[wire_id % num_wires]
                target = wires[(wire_id + 1) % num_wires]
            if layer % 2 == 0:
                control = wires[(wire_id + 1) % num_wires]
                target = wires[wire_id % num_wires]
            qml.CNOT(wires = [control , target])

    def phase_rotation(params):
        for i in range(num_wires):
            qml.PhaseShift(params[i], wires[i])
    def two_local(params):
        if (params.shape != (num_rep + 1, num_wires)):
            raise ValueError(f"Parameters not of correct size, expected {(num_rep + 1, num_wires)}, got {params.shape}")
        phase_rotation(params[0])
        for layer in range(1, num_rep + 1):
            if entanglement_type == SCA:
                sca_entanglement_layer(layer)
            else:
                entanglement_layer()
            phase_rotation(params[layer])
    return two_local