"""Estimate delay from the two white-noise recordings in the SMARD 2000 ZIP."""
import argparse
from io import BytesIO
from pathlib import Path
from zipfile import ZipFile

from matplotlib.figure import Figure
import soundfile as sf

from pyacdete.loudspeaker import estimate_delay


RECORDING_FOLDER = "2000_20140121-1125"
REFERENCE_FILE = "wgn_48kHz_ch8_DirLS.flac"
MICROPHONE_FILE = "wgn_48kHz_ch24_single_mic.flac"
SAMPLE_RATE = 48_000
START_SAMPLE = 48_000
FRAME_COUNT = 4_800


def read_window(archive, filename):
    with BytesIO(archive.read(f"{RECORDING_FOLDER}/{filename}")) as recording:
        samples, fs = sf.read(recording, start=START_SAMPLE, frames=FRAME_COUNT,
                              dtype="float64")
    if fs != SAMPLE_RATE or samples.shape != (FRAME_COUNT,):
        raise ValueError(f"Expected {FRAME_COUNT} mono samples at {SAMPLE_RATE} Hz from {filename}")
    return samples


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("archive", type=Path, help="Path to the official SMARD 2000.zip raw archive")
    parser.add_argument("--output", type=Path, default=Path("smard-delay-correlation.png"),
                        help="Output PNG path")
    args = parser.parse_args()

    with ZipFile(args.archive) as archive:
        reference = read_window(archive, REFERENCE_FILE)
        microphone = read_window(archive, MICROPHONE_FILE)
    result = estimate_delay(reference, microphone, SAMPLE_RATE)

    lag = result["lag_samples"]
    delay_ms = 1000 * result["delay_seconds"]
    lags_ms = 1000 * result["lags_samples"] / SAMPLE_RATE
    correlation = result["correlation"]
    peak = correlation[lag - result["lags_samples"][0]]

    figure = Figure(figsize=(9, 5.5), layout="constrained")
    overview, detail = figure.subplots(2, 1)
    figure.suptitle("SMARD 2000 · White Gaussian noise · Channel 8 → Channel 24")
    for axis in (overview, detail):
        axis.plot(lags_ms, correlation, color="#1762a3", linewidth=1)
        axis.axvline(delay_ms, linestyle="--", color="#ad451e", linewidth=1)
        axis.plot(delay_ms, peak, "o", color="#ad451e", markersize=5)
        axis.set(xlabel="Lag (ms)", ylabel="Cross-correlation (raw sum)")
        axis.grid(alpha=0.24)
    overview.set_title("Full lag range", loc="left")
    detail.set(title=f"Peak at {delay_ms:+.3f} ms ({lag:+d} samples)",
               xlim=(delay_ms - 2, delay_ms + 2))
    figure.savefig(args.output, dpi=160, format="png")

    print(f"Estimated lag: {lag:+d} samples")
    print(f"Estimated delay: {delay_ms:+.3f} ms")
    print(f"Peak correlation: {peak:.6f}")
    print(f"Saved {args.output}")


if __name__ == "__main__":
    main()
