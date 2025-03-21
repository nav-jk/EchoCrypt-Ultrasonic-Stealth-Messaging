import numpy as np
import sounddevice as sd
import time

# Parameters
fs = 22050  # Sampling rate
symbol_duration = 0.1  # Symbol duration
preamble_duration = 1  # Preamble duration
preamble_freqs = [400, 600]  # Audible preamble frequencies
repeat_count = 3  # Repeat the message multiple times

# FSK Frequency Mapping
freq_map = {
    '00': 500,
    '01': 700,
    '10': 900,
    '11': 1200
}

def generate_tone(frequency, duration, volume=80):
    """Generates a loud sine wave of the given frequency and duration."""
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    tone = volume * np.sin(2 * np.pi * frequency * t)  
    return np.column_stack((tone, tone))  # Stereo output

def transmit_preamble():
    """Transmits an alternating preamble tone."""
    print("🔊 Transmitting preamble...")
    signal = np.concatenate([generate_tone(f, symbol_duration) for f in preamble_freqs])
    for _ in range(int(preamble_duration / (2 * symbol_duration))):
        sd.play(signal, samplerate=fs)
        sd.wait()
        time.sleep(0.05)  

def text_to_binary(text):
    """Converts text to binary."""
    return ''.join(format(ord(char), '08b') for char in text)

def transmit_text(message):
    """Encodes and transmits a message multiple times using FSK."""
    binary_message = text_to_binary(message)
    
    # Ensure length is a multiple of 2
    while len(binary_message) % 2 != 0:
        binary_message += '0'
    
    # Convert binary into 2-bit chunks
    symbols = [binary_message[i:i+2] for i in range(0, len(binary_message), 2)]
    
    print(f"📡 Transmitting message: {message}")

    for _ in range(repeat_count):  # Repeat message transmission
        transmit_preamble()
        
        for symbol in symbols:
            freq = freq_map[symbol]
            tone = generate_tone(freq, symbol_duration)
            sd.play(tone, samplerate=fs)
            sd.wait()
            time.sleep(0.03)  

# Example usage
message = "Hello"
transmit_text(message)
