"""
Simple script to generate a beep sound for alert (without SciPy)
"""
import numpy as np
import wave
import os

# Audio parameters
sample_rate = 44100  # Hz
duration = 1.0  # seconds
frequency = 1000  # Hz (beep tone)

# Generate time array
t = np.linspace(0, duration, int(sample_rate * duration))

# Generate sine wave for beep
amplitude = 0.5
beep = amplitude * np.sin(2 * np.pi * frequency * t)

# Add envelope to prevent clicking
envelope = np.ones_like(t)
fade_samples = int(0.01 * sample_rate)  # 10ms fade
envelope[:fade_samples] = np.linspace(0, 1, fade_samples)
envelope[-fade_samples:] = np.linspace(1, 0, fade_samples)
beep = beep * envelope

# Convert to 16-bit integer
beep_int = np.int16(beep * 32767)

# Create assets directory if it doesn't exist
assets_dir = os.path.join(os.path.dirname(__file__), 'frontend', 'assets')
os.makedirs(assets_dir, exist_ok=True)

# Save as WAV file
output_path = os.path.join(assets_dir, 'alert-sound.wav')

# Write WAV file
with wave.open(output_path, 'w') as wav_file:
    wav_file.setnchannels(1)  # Mono
    wav_file.setsampwidth(2)  # 16-bit
    wav_file.setframerate(sample_rate)
    wav_file.writeframes(beep_int.tobytes())

print(f"[OK] Alert sound generated: {output_path}")
