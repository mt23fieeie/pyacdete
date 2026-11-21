"""Loudspeaker frequency response and harmonic distortion measurements."""
import csv
from pathlib import Path
import warnings

import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

__all__ = ["h1_response", "single_tone_thd"]


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


def single_tone_thd(mic_samples, fs, f0, max_order=3):
    """Estimate fundamental-referenced THD from a steady single-tone recording.

    Compare harmonics through max_order and 3 * max_order, limited to
    frequencies below Nyquist. Use the extended estimate when it exceeds
    the baseline by more than 10 percent, and emit a RuntimeWarning.
    The result includes both estimates, the selected and checked orders,
    and the frequencies and peak amplitudes through the selected order.
    """
    for name, value in (("fs", fs), ("f0", f0)):
        if (not np.isscalar(value) or np.asarray(value).dtype.kind not in "iuf"
                or not np.isfinite(value) or value <= 0):
            raise ValueError(f"{name} must be a positive finite frequency in Hz")
    fs, f0 = float(fs), float(f0)
    if not np.isfinite(fs) or not np.isfinite(f0) or fs <= 0 or f0 <= 0:
        raise ValueError("fs and f0 must be representable as positive finite floats")
    if (isinstance(max_order, (bool, np.bool_))
            or not isinstance(max_order, (int, np.integer)) or max_order < 2):
        raise ValueError("max_order must be an integer >= 2")
    max_order = int(max_order)
    nyquist = fs / 2
    if 2 * f0 >= nyquist:
        raise ValueError("the second harmonic must be below the Nyquist frequency")

    samples = np.asarray(mic_samples)
    if samples.ndim != 1 or samples.size == 0 or samples.dtype.kind not in "iuf":
        raise ValueError("mic_samples must be a nonempty 1D array of real numeric samples")
    with np.errstate(over="ignore", invalid="ignore"):
        samples = samples.astype(float, copy=False)
    if not np.all(np.isfinite(samples)):
        raise ValueError("mic_samples must contain only finite samples")
    cycles = f0 / fs * samples.size
    if cycles < 1 and not np.isclose(cycles, 1, rtol=0, atol=1e-8):
        raise ValueError("mic_samples must span at least one complete fundamental cycle")
    scale = np.max(np.abs(samples))
    if scale == 0:
        raise ValueError("mic_samples has no usable fundamental at f0")

    # A candidate at the boundary can arise from an integer Nyquist/f0 ratio.
    orders = np.arange(1, min(3 * max_order, int(nyquist / f0)) + 1)
    orders = orders[orders * f0 < nyquist]
    checked_order = int(orders[-1])
    base_order = min(max_order, checked_order)
    frequencies = orders * f0
    scaled_samples = samples / scale
    scaled_samples -= scaled_samples.mean()
    fundamental_bin = round(cycles)
    if (np.isclose(cycles, fundamental_bin, rtol=0, atol=1e-8)
            and checked_order * fundamental_bin < samples.size / 2):
        spectrum = np.fft.rfft(scaled_samples)
        amplitudes = (2 / samples.size) * np.abs(spectrum[orders * fundamental_bin])
    else:
        # The window's main lobe extends about four original FFT bins
        # on either side of a tone. Keep adjacent harmonics outside it.
        if cycles < 4:
            raise ValueError("off-bin analysis requires at least four fundamental cycles")
        window = signal.windows.blackmanharris(samples.size, sym=False)
        fft_size = 8 * samples.size
        spectrum = np.abs(np.fft.rfft(scaled_samples * window, n=fft_size))
        amplitudes = (2 / window.sum()) * np.interp(
            8 * cycles * orders, np.arange(spectrum.size), spectrum
        )

    # Ignore floating-point residue on bins with no measurable component.
    numerical_floor = 8 * np.finfo(float).eps * np.log2(samples.size)
    amplitudes[amplitudes <= numerical_floor] = 0
    fundamental = amplitudes[0]
    if fundamental == 0:
        raise ValueError("mic_samples has no usable fundamental at f0")

    thd_base = float(100 * np.linalg.norm(amplitudes[1:base_order]) / fundamental)
    thd_extended = float(100 * np.linalg.norm(amplitudes[1:]) / fundamental)
    small, big = sorted((thd_base, thd_extended))
    use_extended = big > 1.10 * small
    used_order = checked_order if use_extended else base_order
    with np.errstate(over="ignore"):
        peak_amplitudes = amplitudes[:used_order] * scale
    if not np.all(np.isfinite(peak_amplitudes)):
        raise ValueError("harmonic amplitudes overflowed; check sample units")
    if use_extended:
        warnings.warn(
            f"Higher-order harmonics increase THD from {thd_base:.6g}% to "
            f"{thd_extended:.6g}% and may indicate stronger nonlinear behavior "
            f"under these measurement conditions. Using orders 2 through {used_order}.",
            RuntimeWarning,
            stacklevel=2,
        )

    return dict(
        harmonic_order=orders[:used_order],
        frequency_hz=frequencies[:used_order],
        amplitude_peak=peak_amplitudes,
        thd_percent=thd_extended if use_extended else thd_base,
        thd_base_percent=thd_base,
        thd_extended_percent=thd_extended,
        max_order_used=used_order,
        max_order_checked=checked_order,
    )
