"""Analyze the 1 kHz step in SMARD configuration 2000 (Nielsen et al., IWAENC 2014)."""

from pathlib import Path

import soundfile as sf
from pyacdete.loudspeaker import single_tone_thd

recording = Path(__file__).with_name("sinus_tones_48kHz_ch24_single_mic.flac")
# Samples from 9.200 s up to 9.700 s at 48 kHz.
mic_samples, fs = sf.read(recording, start=441_600, stop=465_600)
f0 = 1_000
result = single_tone_thd(mic_samples, fs, f0, max_order=3)

amplitudes = result["amplitude_peak"]
for order, amplitude in enumerate(amplitudes, start=1):
    print(f"H{order} ({order * f0} Hz): {amplitude:.6g}")
print(f"THD (H2-H{len(amplitudes)}): {result['thd_percent']:.4f}%")
