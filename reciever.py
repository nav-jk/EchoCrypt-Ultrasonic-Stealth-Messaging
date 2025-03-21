import numpy as np
import sounddevice as sd
import collections

# Parameters
fs = 22050  # Sampling rate
symbol_duration = 0.15  # Symbol duration
preamble_duration = 1  # Preamble duration
preamble_freqs = [400, 600]  # Detectable preamble frequencies
repeated_threshold = 2  # Minimum occurrences for message validity

# FSK Frequency Mapping
freq_map = {
    500: '00',
    700: '01',
    900: '10',
    1200: '11'
}

def record_audio(duration):
    """Records audio for a given duration."""
    print(f"🎤 Recording for {duration} seconds...")
    recording = sd.rec(int(fs * duration), samplerate=fs, channels=1, dtype='float32')
    sd.wait()
    return recording.flatten()

def detect_preamble(audio):
    """Detects the preamble tones in the recorded audio."""
    print("🔎 Searching for preamble...")
    fft = np.abs(np.fft.rfft(audio))
    freqs = np.fft.rfftfreq(len(audio), 1 / fs)
    
    detected = any(np.isclose(freqs[np.argmax(fft)], f, atol=20) for f in preamble_freqs)
    if detected:
        print("✅ Preamble detected!")
    return detected

def extract_frequencies(audio):
    """Extracts dominant frequencies from each symbol duration."""
    num_samples = int(symbol_duration * fs)
    symbols = []
    
    for i in range(0, len(audio), num_samples):
        chunk = audio[i:i + num_samples]
        if len(chunk) < num_samples:
            break

        fft = np.abs(np.fft.rfft(chunk))
        freqs = np.fft.rfftfreq(len(chunk), 1 / fs)
        dominant_freq = freqs[np.argmax(fft)]

        # Match to the closest known frequency
        closest_freq = min(freq_map.keys(), key=lambda f: abs(f - dominant_freq))
        symbols.append(freq_map[closest_freq])

    return ''.join(symbols)

def binary_to_text(binary_string):
    """Converts binary to text."""
    chars = [binary_string[i:i+8] for i in range(0, len(binary_string), 8)]
    text = ''.join(chr(int(c, 2)) for c in chars if len(c) == 8)
    return text

def receive_text():
    """Receives and decodes a repeated FSK message and reconstructs the original text."""
    received_messages = collections.Counter()
    
    print("🎤 Listening for transmissions...")
    
    for _ in range(5):  # Try receiving multiple times
        audio = record_audio(preamble_duration)
        
        if detect_preamble(audio):
            audio = record_audio(5)  
            binary_message = extract_frequencies(audio)
            text_message = binary_to_text(binary_message)
            
            if text_message:
                received_messages[text_message] += 1
                print(f"📩 Partial message received: {text_message}")

    # Find the most frequently received message
    if received_messages:
        final_message = max(received_messages, key=received_messages.get)
        print(f"✅ Final decoded message: {final_message}")
    else:
        print("❌ No valid message received.")

# Example usage
receive_text()
