"""Run from the directory containing the configuration 2000 FLAC recordings."""
from pathlib import Path
import soundfile as sf
from pyacdete.loudspeaker import h1_response


if __name__ == "__main__":
    folder = Path.cwd()
    x, fs = sf.read(folder / "wgn_48kHz_ch8_DirLS.flac", dtype="float64")
    y, fs_y = sf.read(folder / "wgn_48kHz_ch24_single_mic.flac", dtype="float64")
    if fs != fs_y:
        raise ValueError("Reference and microphone sampling rates differ.")
    print(f"fs = {fs} Hz; reference duration = {len(x) / fs:.3f} s")
    result = h1_response(x, y, fs, mode="both", threshold=0.9,
                         save_path=folder / "smard_h1_response.csv")
    print(f"Welch nperseg = {result['nperseg']}")
    print(f"Accepted frequency bins = {result['valid'].sum()} / {len(result['valid'])}")
