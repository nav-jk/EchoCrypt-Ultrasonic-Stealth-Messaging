import numpy as np
import sounddevice as sd
import time

# Parameters
fs = 22050  # Sampling rate
symbol_duration = 0.15  # Increase duration for stability
preamble_duration = 1  # 1 second preamble
preamble_freqs = [400, 600]  # Audible preamble
ack_freq = 1000  # Acknowledgment tone

# FSK Mapping (Audible)
freq_map = {
    '00': 500,
    '01': 700,
    '10': 900,
    '11': 1200
}

def generate_tone(frequency, duration, volume=100):
    """Generates a loud sine wave of the given frequency and duration."""
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    tone = volume * np.sin(2 * np.pi * frequency * t)
    return np.column_stack((tone, tone))  # Stereo output

def transmit_preamble():
    """Transmits an alternating preamble tone to initiate communication."""
    print("🔊 Transmitting preamble...")
    signal = np.concatenate([generate_tone(f, symbol_duration) for f in preamble_freqs])
    for _ in range(int(preamble_duration / (2 * symbol_duration))):
        sd.play(signal, samplerate=fs)
        sd.wait()
        time.sleep(0.05)

def receive_acknowledgment():
    """Listens for the receiver's acknowledgment signal (ACK)."""
    duration = 1  # Listen for 1 second
    print("👂 Waiting for ACK...")
    recording = sd.rec(int(fs * duration), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    
    # FFT to detect dominant frequency
    fft = np.abs(np.fft.rfft(recording.flatten()))
    freqs = np.fft.rfftfreq(len(recording), 1 / fs)
    
    if np.isclose(freqs[np.argmax(fft)], ack_freq, atol=20):
        print("✅ ACK received! Proceeding with message transmission...")
        return True
    print("❌ No ACK received. Retrying...")
    return False

def text_to_binary(text):
    """Converts text to binary."""
    return ''.join(format(ord(char), '08b') for char in text)

def transmit_text(message):
    """Encodes and transmits a message using FSK."""
    binary_message = text_to_binary(message)
    
    # Pad to ensure length is a multiple of 2
    while len(binary_message) % 2 != 0:
        binary_message += '0'
    
    symbols = [binary_message[i:i+2] for i in range(0, len(binary_message), 2)]
    
    print(f"📡 Transmitting message: {message}")
    
    # Step 1: Transmit Preamble and Wait for ACK
    while True:
        transmit_preamble()
        if receive_acknowledgment():
            break  # Proceed if ACK received
    
    # Step 2: Transmit Symbols
    for symbol in symbols:
        freq = freq_map[symbol]
        tone = generate_tone(freq, symbol_duration)
        sd.play(tone, samplerate=fs)
        sd.wait()
        time.sleep(0.03)

# Example usage
message = "Hello"
transmit_text(message)
