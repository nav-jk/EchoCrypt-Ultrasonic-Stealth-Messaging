import numpy as np
import sounddevice as sd
import scipy.signal as signal

# Parameters
fs = 22050  # Must match transmitter sampling rate
symbol_duration = 0.15  # Duration per symbol
preamble_duration = 1  # Preamble detection time
preamble_freqs = [400, 600]  # Detect these tones
ack_freq = 1000  # Acknowledgment signal

# FSK Mapping
freq_map = {
    500: '00',
    700: '01',
    900: '10',
    1200: '11'
}

def generate_tone(frequency, duration, volume=100):
    """Generates a loud sine wave of the given frequency and duration."""
    t = np.linspace(0, duration, int(fs * duration), endpoint=False)
    tone = volume * np.sin(2 * np.pi * frequency * t)
    return np.column_stack((tone, tone))  # Stereo output

def record_audio(duration):
    """Records audio for a given duration."""
    print(f"🎤 Recording for {duration} seconds...")
    recording = sd.rec(int(fs * duration), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    return recording.flatten()

def detect_preamble(audio):
    """Detects the preamble tones."""
    print("🔎 Searching for preamble...")
    fft = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(len(audio), 1 / fs)
    
    detected = any(np.isclose(freqs[np.argmax(fft)], f, atol=20) for f in preamble_freqs)
    if detected:
        print("✅ Preamble detected!")
    return detected

def send_acknowledgment():
    """Sends an ACK signal back to the transmitter."""
    print("📡 Sending ACK...")
    tone = generate_tone(ack_freq, 0.5)
    sd.play(tone, samplerate=fs)
    sd.wait()

def extract_frequencies(audio):
    """Extracts dominant frequency in each symbol duration."""
    num_samples = int(symbol_duration * fs)
    symbols = []
    
    for i in range(0, len(audio), num_samples):
        chunk = audio[i:i + num_samples]
        if len(chunk) < num_samples:
            break

        fft = np.abs(np.fft.rfft(chunk))
        freqs = np.fft.rfftfreq(len(chunk), 1 / fs)
        dominant_freq = freqs[np.argmax(fft)]

        # Match to the closest frequency
        closest_freq = min(freq_map.keys(), key=lambda f: abs(f - dominant_freq))
        symbols.append(freq_map[closest_freq])

    return ''.join(symbols)

def binary_to_text(binary_string):
    """Converts binary to text."""
    chars = [binary_string[i:i+8] for i in range(0, len(binary_string), 8)]
    text = ''.join(chr(int(c, 2)) for c in chars if len(c) == 8)
    return text

def receive_text():
    """Receives and decodes a transmitted FSK message."""
    print("🎤 Listening for preamble...")
    
    # Step 1: Listen for the Preamble
    audio = record_audio(preamble_duration)
    
    if not detect_preamble(audio):
        print("❌ No preamble detected. Aborting.")
        return
    
    # Step 2: Send ACK to Transmitter
    send_acknowledgment()
    
    # Step 3: Record and Decode Message
    audio = record_audio(5)  # Record for 5 seconds
    binary_message = extract_frequencies(audio)
    text_message = binary_to_text(binary_message)
    
    print(f"📩 Received message: {text_message}")

# Example usage
receive_text()
