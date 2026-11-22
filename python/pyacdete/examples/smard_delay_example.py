"""Measure and plot the loopback-to-microphone delay in SMARD configuration 2000."""

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import soundfile as sf
from pyacdete.loudspeaker import cross_correlation_delay


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("audio_folder", type=Path, help="Folder containing the two SMARD FLAC files")
    folder = parser.parse_args().audio_folder

    x, fs = sf.read(folder / "wgn_48kHz_ch8_DirLS.flac")
    y, _ = sf.read(folder / "wgn_48kHz_ch24_single_mic.flac")

    result = cross_correlation_delay(x, y, fs, return_correlation=True)
    delay_samples = result["delay_samples"]
    delay_seconds = result["delay_seconds"]
    delay_ms = 1000 * delay_seconds

    print(f"Sample rate: {fs} Hz")
    print(f"Samples per channel: {x.size}")
    print(f"Delay: {delay_samples:+d} samples")
    print(f"Delay: {delay_seconds:+.9f} s ({delay_ms:+.6f} ms)")

    lags_ms = result["lags_samples"] * (1000 / fs)
    correlation = result["correlation"]
    left_ms = min(0, delay_ms) - 5
    right_ms = max(0, delay_ms) + 5
    visible = (lags_ms >= left_ms) & (lags_ms <= right_ms)

    fig, ax = plt.subplots(figsize=(9, 4.5), layout="constrained")
    ax.plot(lags_ms[visible], correlation[visible], color="#175f9c", linewidth=1)
    ax.axvline(delay_ms, color="#bd3b26", linestyle="--", linewidth=1.2,
               label=f"Peak at {delay_samples:+d} samples ({delay_ms:+.3f} ms)")
    ax.scatter(delay_ms, correlation.max(), color="#bd3b26", s=28, zorder=3)
    ax.set(title="SMARD 2000 loopback-to-microphone cross-correlation",
           xlabel="Lag (ms)", ylabel="Cross-correlation", xlim=(left_ms, right_ms))
    ax.grid(alpha=0.2)
    ax.legend(loc="upper left")

    output = Path(__file__).with_name("smard_delay_correlation.png")
    fig.savefig(output, dpi=180)
    plt.close(fig)
    print(f"Plot saved: {output.name}")


if __name__ == "__main__":
    main()
