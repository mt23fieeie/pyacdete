"""A single-function H1 API: calculate, plot, and save selected responses."""
import csv
from pathlib import Path
import warnings

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

__all__ = ["h1_response"]


def h1_response(x, y, fs, *, mode="both", threshold=0.9,
                nperseg=None, save_path="response.csv"):
    """Estimate H1 magnitude/phase from synchronized reference x and output y.

    mode: "magnitude", "phase", or "both".
    threshold: minimum magnitude-squared coherence for displayed/exported data.
    nperseg: Welch segment length; None chooses a starting value automatically.
    save_path: CSV path, or None to skip saving.

    Uses the original magnitude_response_principle_1.py and
    phase_response_principle_1.py calculation steps, with user-supplied x/y.
    Returns frequency_hz, coherence, valid, nperseg, and the selected
    magnitude_db/phase_deg arrays in a dictionary. Rejected values are NaN
    in arrays, blank in CSV, and gaps in plots. Close the plot to return.
    Magnitude is transfer gain, not dB SPL. Phase retains measurement delay.
    """
    if mode not in ("magnitude", "phase", "both"):
        raise ValueError('mode must be "magnitude", "phase", or "both"')
    if isinstance(fs, (bool, np.bool_)) or not np.isscalar(fs) or not np.isreal(fs) or not np.isfinite(fs) or fs <= 0:
        raise ValueError("fs must be a positive finite sampling frequency")
    if not np.isscalar(threshold) or not np.isreal(threshold) or not np.isfinite(threshold) or not 0 <= threshold <= 1:
        raise ValueError("threshold must be between 0 and 1")
    x, y = np.asarray(x), np.asarray(y)
    if x.ndim != 1 or y.ndim != 1 or x.size != y.size or x.size == 0:
        raise ValueError("x and y must be nonempty, equal-length 1D signals")
    if x.dtype.kind not in "iuf" or y.dtype.kind not in "iuf":
        raise ValueError("x and y must contain real numeric samples")
    x, y = x.astype(float), y.astype(float)
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(y)):
        raise ValueError("x and y must contain only finite samples")

    # Target <=0.5 seconds, keeping >=8 complete, half-overlapped segments.
    if nperseg is None:
        limit = min(fs / 2, 2 * len(x) / 9)
        if limit < 4:
            raise ValueError("too little data for automatic Welch settings")
        nperseg = 2 ** int(np.floor(np.log2(limit)))
    if isinstance(nperseg, (bool, np.bool_)) or not isinstance(nperseg, (int, np.integer)) or nperseg < 4:
        raise ValueError("nperseg must be an integer >= 4, or None")
    noverlap = nperseg // 2
    if len(x) < nperseg + (nperseg - noverlap):
        raise ValueError("at least two complete Welch segments are required")
    segments = 1 + (len(x) - nperseg) // (nperseg - noverlap)
    if segments < 8:
        warnings.warn("Fewer than 8 Welch segments; coherence may be optimistic.", stacklevel=2)
    settings = dict(fs=float(fs), window="hann", nperseg=nperseg,
                    noverlap=noverlap, nfft=nperseg, detrend="constant")

    # Original demo core; x is the demo's input u.
    # SciPy csd(x, y) uses conj(X)*Y: delayed output has negative phase slope.
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        f, Suu = signal.welch(x, **settings)
        _, Syu = signal.csd(x, y, **settings)
    if not np.all(np.isfinite(Suu)) or not np.all(np.isfinite(Syu)):
        raise ValueError("spectral estimates overflowed; check sample units")
    if Suu.max() <= 0:
        raise ValueError("x has no usable reference energy after detrending")
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        H1 = Syu / Suu
    if not np.all(np.isfinite(H1)):
        raise ValueError("H1 is undefined; check for zero reference PSD or numerical overflow")

    # Original demo magnitude, phase, coherence, and masking order.
    magnitude = np.abs(H1)
    magnitude_db = 20 * np.log10(np.maximum(magnitude, 1e-12))
    phi_wrapped = np.angle(H1)
    phi = np.unwrap(phi_wrapped)
    phase_deg = np.degrees(phi)
    with np.errstate(over="ignore", invalid="ignore", divide="ignore"):
        _, C = signal.coherence(x, y, **settings)
    valid = C >= threshold
    result = dict(frequency_hz=f, coherence=C, valid=valid, nperseg=int(nperseg))
    curves = {}
    if mode in ("magnitude", "both"):
        result["magnitude_db"] = np.where(valid, magnitude_db, np.nan)
        curves["magnitude_db"] = "Magnitude (dB re transfer gain 1)"
    if mode in ("phase", "both"):
        result["phase_deg"] = np.where(valid, phase_deg, np.nan)
        curves["phase_deg"] = "Unwrapped phase (degree)"
    if not np.any(valid):
        warnings.warn("No accepted response bins; inspect coherence and input data.", stacklevel=2)

    if save_path is not None:
        columns = ["frequency_hz", "coherence", *curves]
        with Path(save_path).open("w", newline="", encoding="utf-8") as stream:
            writer = csv.writer(stream)
            writer.writerow(columns)
            writer.writerows([float(v) if np.isfinite(v) else "" for v in row]
                             for row in zip(*(result[key] for key in columns)))

    fig, axes = plt.subplots(1 + len(curves), 1, sharex=True,
                              figsize=(10, 3 * (1 + len(curves))))
    axes[0].plot(f, C)
    axes[0].axhline(threshold, color="red", linestyle="--", label=f"Threshold = {threshold}")
    axes[0].set(ylabel="Coherence C", ylim=(0, 1.05), title="H1 response")
    axes[0].legend()
    for ax, (key, label) in zip(axes[1:], curves.items()):
        ax.plot(f, result[key])
        ax.set_ylabel(label)
    for ax in axes:
        ax.grid(True)
    axes[-1].set(xlabel="Frequency (Hz)", xlim=(0, float(fs) / 2))
    fig.tight_layout()
    plt.show()
    return result
