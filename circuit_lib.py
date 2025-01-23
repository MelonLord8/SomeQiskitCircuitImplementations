import pennylane as qml
from math import pi
FULL = "full"
LINEAR = "linear"
REVERSE_LINEAR = "reverse_linear"
PAIRWISE = "pairwise"
CIRCULAR = "circular"
SCA = "sca"

def create_TwoLocal(device, num_reps = 1, entanglement_type = LINEAR):
    """
    Creates a circuit identical to qiskit.circuit.library.TwoLocal

    args:
    - device : Device this function will be used on
    - num_reps : How many times this will be repeated (default is one) 
    - entanglement_type : What type of entanglement will be used (default is linear)

    returns:
    A TwoLocal function tailored to the device
    """

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
        if (params.shape != (num_reps + 1, num_wires)):
            raise ValueError(f"Parameters not of correct size, expected {(num_reps + 1, num_wires)}, got {params.shape}")
        phase_rotation(params[0])
        for layer in range(1, num_reps + 1):
            if entanglement_type == SCA:
                sca_entanglement_layer(layer)
            else:
                entanglement_layer()
            phase_rotation(params[layer])
    return two_local

def create_ZZFeatureMap(device, wires = None, num_reps = 1):
    """
    Creates a circuit indentical to qiskit.circuit.libary.ZZFeatureMap
    So far only implements full entanglement.

    Args :
    - device : Device this function will be used on
    - wires : wires this feature map will act on, (if not all wires on device)
    - num_reps : how many times this will be repeated (default is one)

    Please note that the features given to ZZFeature map must have the same size as the number of wires specified.

    Returns :
    A ZZFeatureMap function tailored to the device
    """

    if wires == None:
        wires = device.wires
    feature_size = len(wires)
    if num_reps < 1:
        raise ValueError(f"At least one repitition required")
    
    def phase1(feature):
        return 2*feature
    def phase2(feature1, feature2):
        return 2*(pi - feature1)*(pi - feature2)
    
    def initial_gates(features):
        for i in range(feature_size):
            qml.H(wires = wires[i])
            qml.PhaseShift(phase1(features[i]), wires= wires[i])

    def ZZgate(i,j, feature1, feature2):
        qml.CNOT(wires = [wires[j], wires[i]])
        qml.PhaseShift(phase2(feature1, feature2), wires = wires[i])
        qml.CNOT(wires = [wires[j], wires[i]])

    def ZZgates(features):
        for i in range(1, feature_size):
            for j in range(i):
                ZZgate(i,j,features[i], features[j])

    def ZZFeatureMap(features):
        if len(features) != feature_size:
            raise ValueError(f"Feature size incorrect, expected features of size {feature_size}, got {len(features)}")
        for i in range(num_reps):
            initial_gates(features)
            ZZgates(features)

    return ZZFeatureMap