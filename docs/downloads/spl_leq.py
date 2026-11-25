r"""Unweighted equivalent continuous sound pressure level from mono recordings.
单声道（mono）：每段录音只有一个音频通道。在本项目里：一个测量麦克风录到的波形。
未加权（unweighted）：计算时，各频率按录到的幅度计入。
等效连续声压级（\(L_{\mathrm{eq}}\)）：用一个恒定的声压级概括整段录音。
"""

from math import inf, log10

import numpy as np


def _rms(samples):
    x = np.asarray(samples, dtype=np.float64)
    if x.ndim != 1 or x.size == 0:
        raise ValueError("Expected a nonempty mono recording.")
    return float(np.sqrt(np.mean(x**2)))


def _amplitude_db(ratio):
    return -inf if ratio == 0 else 20 * log10(ratio)


def spl_leq(mic_samples, fs, *, calibration=None):
    """Measure a selected mono recording segment using Miyara's Eq. (7.7).

    Pass finite one-dimensional samples and the test sampling rate fs in Hz.
    For absolute SPL, pass calibration as (cal_samples, level_db_spl) from the same microphone chain.

    Returns duration_s, rms, and leq_db_spl.
    leq_db_spl is None when calibration is omitted.
    """
    test_rms = _rms(mic_samples)
    leq_db_spl = None
    if calibration is not None:
        cal_samples, level_db_spl = calibration
        cal_rms = _rms(cal_samples)
        if cal_rms <= 0 or not np.isfinite(cal_rms):
            raise ValueError("Calibration signal is invalid.")

        leq_db_spl = float(level_db_spl + _amplitude_db(test_rms / cal_rms))

    return {
        "duration_s": float(len(mic_samples) / fs),
        "rms": test_rms,
        "leq_db_spl": leq_db_spl,
    }
