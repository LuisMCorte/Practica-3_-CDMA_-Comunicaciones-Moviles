import numpy as np
import math

# =========================
# GENERACIÓN DE CÓDIGOS
# =========================

def hadamard_matrix(n):
    if n == 1:
        return np.array([[1]])
    H = hadamard_matrix(n // 2)
    top = np.hstack((H, H))
    bottom = np.hstack((H, -H))
    return np.vstack((top, bottom))


def hadamard_to_binary(H):
    # +1 -> 0, -1 -> 1
    return np.where(H == 1, 0, 1)


def assign_codes(num_users):
    N = 2**math.ceil(math.log2(num_users))
    H = hadamard_matrix(N)
    return hadamard_to_binary(H[:num_users])


# =========================
# PROCESAMIENTO
# =========================

def bits_to_bipolar(bits):
    return np.array([1 if b == 0 else -1 for b in bits])


def spread_signal_xor(bits, code):
    spread = []
    for bit in bits:
        spread.extend([bit ^ chip for chip in code])
    return spread


# =========================
# TRANSMISOR
# =========================

def cdma_transmitter(users, num_bits):
    
    codes = assign_codes(users)
    data = np.random.randint(0, 2, size=(users, num_bits))

    all_signals = []

    for i in range(users):
        spread = spread_signal_xor(data[i], codes[i])
        signal = bits_to_bipolar(spread)
        all_signals.append(signal)

    combined_signal = np.sum(all_signals, axis=0)

    return data, codes, all_signals, combined_signal