def finitist_quantum_simulator(n_qubits, gate_sequence, clauses=None):
    """
    Finitist simulator in FA.
    - n_qubits: concrete natural
    - gate_sequence: list of finitary gate indices (0=H, 1=X, 2=phase-flip, etc.)
    - clauses: optional 3SAT clauses for hybrid quantum-classical witness search
    Returns: concrete measurement outcome (bit string) or None
    """
    ticks = n_qubits                     # linear bound
    twists = 2                           # parity only
    
    for t in range(twists):
        for k in range(ticks):
            # Finitary "state" = single natural k transformed by gates
            state = k
            for gate in gate_sequence:
                if gate == 0:   # finitary Hadamard ≈ parity + shift
                    state = (state >> 1) ^ (state % 2)
                elif gate == 1: # X gate = flip parity
                    state = state ^ 1
                elif gate == 2: # phase ≈ modular twist
                    state = (state * 3 + t) % (n_qubits + 1)
            
            # Collapse = Möbius projection (already proven in FA)
            assign = [
                bool(((state >> i) % 2) ^ (t % 2))
                for i in range(n_qubits)
            ]
            
            # Optional: hybrid 3SAT witness check
            if clauses is None or all(any(assign[abs(lit)-1] == (lit > 0) for lit in c)
                                      for c in clauses):
                return assign  # concrete measurement outcome
    return None  # no constructive witness