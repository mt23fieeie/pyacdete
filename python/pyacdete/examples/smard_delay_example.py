"""Measure the loopback-to-microphone delay in SMARD configuration 2000."""

import argparse
from pathlib import Path

import soundfile as sf
from pyacdete.loudspeaker import cross_correlation_delay


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio_folder", type=Path, help="Folder containing the two SMARD FLAC files")
    folder = parser.parse_args().audio_folder

    x, fs = sf.read(folder / "wgn_48kHz_ch8_DirLS.flac")
    y, fs_y = sf.read(folder / "wgn_48kHz_ch24_single_mic.flac")
    if fs != fs_y:
        parser.error("The two recordings must use the same sampling rate.")

    result = cross_correlation_delay(x, y, fs)
    print(f"Sample rate: {fs} Hz")
    print(f"Samples per channel: {x.size}")
    print(f"Delay: {result['delay_samples']:+d} samples")
    print(f"Delay: {result['delay_seconds']:+.9f} s ({1000 * result['delay_seconds']:+.6f} ms)")


if __name__ == "__main__":
    main()
