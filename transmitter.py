import numpy as np
import sounddevice as sd
import time

# Parameters
fs = 22050  # Sampling rate
symbol_duration = 0.2  # Longer symbol duration for better clarity
preamble_duration = 1  # Preamble duration
preamble_freqs = [300, 500]  # Audible preamble frequencies
repeat_count = 3  # Repeat the message multiple times
message_amplitude = 1.0  # Maximum loudness
gap_duration = 0.05  # Short silence between symbols

# FSK Frequency Mapping (Lower for better audibility)
freq_map = {
    '00': 400,
    '01': 500,
    '10': 600,
    '11': 700
}

def generate_tone(frequency, duration, volume=message_amplitude, waveform="square"):
    """Generates a loud waveform (square or sine) for better clarity."""
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    
    if waveform == "square":
        tone = volume * np.sign(np.sin(2 * np.pi * frequency * t))
    else:
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
    """Encodes and transmits a message multiple times using FSK in the audible range."""
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
            tone = generate_tone(freq, symbol_duration, waveform="square")
            sd.play(tone, samplerate=fs)
            sd.wait()
            time.sleep(gap_duration)  # Short silence for better clarity


# Example usage
message = "Hello"
transmit_text(message)
