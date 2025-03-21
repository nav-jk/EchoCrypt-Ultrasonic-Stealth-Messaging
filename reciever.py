import scipy.signal as signal
import numpy as np
import sounddevice as sd

# Define sampling frequency and FSK frequency mapping
fs = 44100  # Sampling rate
symbol_duration = 0.05  # 50ms per symbol
freq_map = {'0': 17000, '1': 19000}  # Frequency mapping
reverse_freq_map = {v: k for k, v in freq_map.items()}

# Goertzel Algorithm for Frequency Detection
def goertzel_filter(segment, target_freq):
    N = len(segment)
    k = int(0.5 + (N * target_freq / fs))
    omega = (2.0 * np.pi * k) / N
    coeff = 2.0 * np.cos(omega)
    s1 = s2 = 0.0

    for sample in segment:
        s0 = sample + coeff * s1 - s2
        s2, s1 = s1, s0

    power = s1**2 + s2**2 - coeff * s1 * s2
    return power

def detect_frequency(segment):
    freqs = list(freq_map.values())
    power = {f: goertzel_filter(segment, f) for f in freqs}
    detected_freq = max(power, key=power.get)  # Pick the strongest frequency
    return detected_freq

# Hamming(7,4) Decoding
def hamming_decode(encoded_bits):
    H = np.array([
        [1, 1, 0, 1, 1, 0, 0],
        [1, 0, 1, 1, 0, 1, 0],
        [0, 1, 1, 1, 0, 0, 1]
    ])
    received = np.array([int(b) for b in encoded_bits]).reshape(-1, 7)
    syndrome = (H @ received.T) % 2

    corrected_bits = []
    for i, s in enumerate(syndrome.T):
        if np.any(s):
            error_pos = int(''.join(map(str, s)), 2) - 1
            if 0 <= error_pos < 7:
                received[i, error_pos] ^= 1  
        corrected_bits.extend(received[i, [2, 4, 5, 6]])  # Extract original 4 bits

    return ''.join(str(b) for b in corrected_bits)

# Convert binary to text
def binary_to_text(binary_string):
    chars = [binary_string[i:i+8] for i in range(0, len(binary_string), 8)]
    return ''.join(chr(int(c, 2)) for c in chars if c)

# Real-time M-FSK Receiver
def receive_text(duration=3):
    print("Listening for message...")
    received_audio = sd.rec(int(duration * fs), samplerate=fs, channels=1, dtype=np.float32)
    sd.wait()
    print("Recording Complete.")

    received_signal = received_audio.flatten()
    chunk_size = int(fs * symbol_duration)
    bits = []

    # Decode signal using Goertzel Algorithm
    for i in range(0, len(received_signal), chunk_size):
        segment = received_signal[i:i+chunk_size]
        detected_freq = detect_frequency(segment)
        
        # Use the closest frequency match
        detected_bit = reverse_freq_map.get(detected_freq, None)
        if detected_bit is not None:
            bits.append(detected_bit)

    # Ensure bits are grouped in 7-bit segments before decoding
    if len(bits) % 7 != 0:
        bits = bits[:-(len(bits) % 7)]  # Trim excess bits
    
    # Decode Hamming(7,4)
    corrected_binary = hamming_decode(bits)
    decoded_message = binary_to_text(corrected_binary)
    
    print(f"Received message: {decoded_message}")

# Start listening
receive_text()
