import numpy as np
import sounddevice as sd
import time

# Sampling rate and bit duration
fs = 44100  
symbol_duration = 0.05  # Shorter for multi-bit transmission

# Multi-bit FSK mapping
freq_map = {
    '00': 17000,
    '01': 17500,
    '10': 18000,
    '11': 18500
}

# Corrected Generator Matrix for Hamming(7,4)
G = np.array([
    [1, 0, 0, 0, 1, 1, 0],
    [0, 1, 0, 0, 1, 0, 1],
    [0, 0, 1, 0, 0, 1, 1],
    [0, 0, 0, 1, 1, 1, 1]
])

def hamming_encode(data_bits):
    """Encodes a 4-bit binary string into a 7-bit Hamming(7,4) code."""
    data = np.array([int(b) for b in data_bits]).reshape(1, -1)  # Ensure it's (1,4)
    encoded = (data @ G) % 2  # (1,4) @ (4,7) -> (1,7)
    return ''.join(str(b) for b in encoded.flatten())


# Convert text to binary and apply Hamming(7,4)
def text_to_hamming_binary(text):
    binary_text = ''.join(format(ord(c), '08b') for c in text)
    padded_text = binary_text + ('0' * (4 - (len(binary_text) % 4)))  # Pad to 4-bit multiples
    encoded_text = ''.join(hamming_encode(padded_text[i:i+4]) for i in range(0, len(padded_text), 4))
    return encoded_text

# Generate FSK signal
def generate_fsk_signal(bits):
    freq = freq_map[bits]
    t = np.linspace(0, symbol_duration, int(fs * symbol_duration), endpoint=False)
    return np.sin(2 * np.pi * freq * t)

# Transmit text using M-FSK
def transmit_text(text):
    binary_message = text_to_hamming_binary(text)
    print(f"Transmitting: {text} -> {binary_message}")

    for i in range(0, len(binary_message), 2):  # Transmit 2 bits per symbol
        bit_pair = binary_message[i:i+2]
        if len(bit_pair) < 2:
            bit_pair = bit_pair + '0'  # Pad last symbol if necessary
        signal = generate_fsk_signal(bit_pair)
        sd.play(signal, fs)
        sd.wait()
        time.sleep(0.01)  # Small delay between symbols

# Send a message
message = "Hi"
transmit_text(message)
