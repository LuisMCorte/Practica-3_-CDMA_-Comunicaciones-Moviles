import numpy as np


# =========================
# UTILIDADES
# =========================

def code_to_bipolar(code):
    return np.array([1 if c == 0 else -1 for c in code])


# =========================
# DESPREADING
# =========================

def despread_signal(received_signal, code, num_bits):
    
    code_bipolar = code_to_bipolar(code)
    N = len(code)

    recovered_bits = []

    for i in range(num_bits):
        start = i * N
        end = (i + 1) * N
        segment = received_signal[start:end]

        correlation = np.sum(segment * code_bipolar)

        if correlation >= 0:
            recovered_bits.append(0)
        else:
            recovered_bits.append(1)

    return np.array(recovered_bits)


# =========================
# RECEPTOR
# =========================

def cdma_receiver(combined_signal, codes, num_bits):
    
    users = len(codes)
    recovered_data = []

    for i in range(users):
        bits = despread_signal(combined_signal, codes[i], num_bits)
        recovered_data.append(bits)

    return np.array(recovered_data)