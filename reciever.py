import numpy as np
import sounddevice as sd
import scipy.signal as signal

# Parameters
fs = 22050  # Must match transmitter sampling rate
symbol_duration = 0.1  # 100 ms per symbol
preamble_duration = 1  # 1 second preamble
preamble_freqs = [400, 600]  # Used for detecting preamble

# Adjusted FSK Mapping for better audibility
freq_map = {
    500: '00',
    700: '01',
    900: '10',
    1200: '11'
}
reverse_freq_map = {v: k for k, v in freq_map.items()}  # Reverse lookup

def record_audio(duration):
    """Records audio for a given duration."""
    print(f"🎤 Recording for {duration} seconds...")
    recording = sd.rec(int(fs * duration), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    return recording.flatten()

def detect_preamble(audio):
    """Detects if the preamble (alternating 400 Hz and 600 Hz tones) is present."""
    print("🔎 Searching for preamble...")
    fft = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(len(audio), 1 / fs)
    
    if any(np.isclose(freqs[np.argmax(fft)], f, atol=20) for f in preamble_freqs):
        print("✅ Preamble detected!")
        return True
    return False

def extract_frequencies(audio):
    """Extracts the dominant frequency in each symbol duration."""
    num_samples = int(symbol_duration * fs)
    symbols = []
    
    for i in range(0, len(audio), num_samples):
        chunk = audio[i:i + num_samples]
        if len(chunk) < num_samples:
            break

        fft = np.abs(np.fft.rfft(chunk))
        freqs = np.fft.rfftfreq(len(chunk), 1 / fs)
        dominant_freq = freqs[np.argmax(fft)]

        # Match to the closest FSK frequency
        closest_freq = min(freq_map.keys(), key=lambda f: abs(f - dominant_freq))
        symbols.append(freq_map[closest_freq])

    return ''.join(symbols)

def binary_to_text(binary_string):
    """Converts a binary string to text."""
    chars = [binary_string[i:i+8] for i in range(0, len(binary_string), 8)]
    text = ''.join(chr(int(c, 2)) for c in chars if len(c) == 8)
    return text

def receive_text():
    """Receives and decodes an FSK-encoded message."""
    audio = record_audio(5)  # Record for 5 seconds
    
    # Step 1: Detect preamble
    if not detect_preamble(audio):
        print("❌ No preamble detected. Aborting.")
        return
    
    # Step 2: Decode FSK symbols
    binary_message = extract_frequencies(audio)

    # Step 3: Convert to text
    text_message = binary_to_text(binary_message)
    
    print(f"📩 Received message: {text_message}")

# Example usage
receive_text()
