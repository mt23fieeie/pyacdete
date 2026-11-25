"""Run spl_leq on Cieslar's calibrated Yamaha MSR400 measurement."""

from io import BytesIO
from pathlib import Path
from urllib.parse import quote
from urllib.request import urlopen

import soundfile as sf

from spl_leq import spl_leq


RECORDINGS_URL = (
    "https://raw.githubusercontent.com/Cieslar-Simon/STI/"
    "1b4a0c33740c52d62b81aad7b667b1f85c522fec/control_measurements/"
)
TEST_RECORDING = "Position 2/STIPA_MES1_P2.wav"
CAL_RECORDING = "Reference_calibration_94_dB_SPL.wav"
CAL_LEVEL_DB_SPL = 94.0


def _read_recording(name):
    local_path = Path(__file__).with_name(Path(name).name)
    if local_path.is_file():
        audio = local_path
    else:
        with urlopen(RECORDINGS_URL + quote(name), timeout=30) as response:
            audio = BytesIO(response.read())
    return sf.read(audio, dtype="float64")


def main():
    mic_samples, fs = _read_recording(TEST_RECORDING)
    cal_samples, fs_cal = _read_recording(CAL_RECORDING)
    result = spl_leq(mic_samples, fs, calibration=(cal_samples, CAL_LEVEL_DB_SPL))
    cal_rms = spl_leq(cal_samples, fs_cal)["rms"]

    print("Yamaha MSR400 | STIPA, Position 2, Measurement 1")
    print(f"Test segment: {result['duration_s']:.3f} s at {fs} Hz")
    print(f"Calibration: 1 kHz, {CAL_LEVEL_DB_SPL:.1f} dB SPL")
    print(f"Test RMS: {result['rms']:.10f}")
    print(f"Calibration RMS: {cal_rms:.10f}")
    print(f"Unweighted Leq: {result['leq_db_spl']:.4f} dB SPL")


if __name__ == "__main__":
    main()
