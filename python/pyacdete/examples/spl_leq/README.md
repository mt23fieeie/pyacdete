# spl_leq and the calibrated loudspeaker example

`spl_leq.py` computes the raw RMS of the selected mono test and calibration recordings and applies Miyara's Eq. (7.7), $L_p=L_{\mathrm{cal}}+20\log_{10}(X_{\mathrm{ef}}/X_{\mathrm{cal}})$. [Published SPL derivation](https://mt23fieie.github.io/pyacdete/spl-leq.html).

## Run the public example

Extract the ZIP and open a terminal in the extracted folder. Use PowerShell on Windows.

```powershell
py -m pip install -r requirements.txt
py sti_spl_example.py
```

On macOS or Linux, use `python3` in place of `py`. The script reads the two WAV files from the directory if present and otherwise downloads them from a pinned copy of the public repository.

| File | Use |
|---|---|
| [STIPA_MES1_P2.wav](https://raw.githubusercontent.com/Cieslar-Simon/STI/1b4a0c33740c52d62b81aad7b667b1f85c522fec/control_measurements/Position%202/STIPA_MES1_P2.wav) | Mono microphone recording of a Yamaha MSR400 loudspeaker playing a STIPA test signal at the second measurement position. Use all 25 s. |
| [Reference_calibration_94_dB_SPL.wav](https://raw.githubusercontent.com/Cieslar-Simon/STI/1b4a0c33740c52d62b81aad7b667b1f85c522fec/control_measurements/Reference_calibration_94_dB_SPL.wav) | Recorded 1 kHz acoustic calibration tone at 94 dB SPL. Use the complete calibration recording. |

The thesis documents the equipment and uses this calibration recording to recover RMS pressure. Both WAVs are 48 kHz mono. The example estimates the broadband unweighted level from the paired WAVs. The source does not specify numerical input gain for individual files or give a broadband unweighted meter reading for this 25 s interval. [Šimon Cieslar, *Computing Speech Transmission Index in Matlab*, §9.2, pp. 68–73 (2025)](https://www.vut.cz/en/students/final-thesis/detail/167229).

```text
Yamaha MSR400 | STIPA, Position 2, Measurement 1
Test segment: 25.000 s at 48000 Hz
Calibration: 1 kHz, 94.0 dB SPL
Test RMS: 0.0254437465
Calibration RMS: 0.3368177544
Unweighted Leq: 71.5637 dB SPL
```

## Measure a captured loudspeaker recording

Select the test interval and a steady segment of the calibration tone. Keep the microphone channel, input gain, and digital scaling the same for both recordings. Pass the known sound pressure level of your calibrator.

```python
import soundfile as sf
from spl_leq import spl_leq

mic_samples, fs = sf.read("loudspeaker.wav", dtype="float64")
cal_samples, _ = sf.read("calibrator.wav", dtype="float64")
result = spl_leq(mic_samples, fs, calibration=(cal_samples, 94.0))
print(result["leq_db_spl"])
```

The WAV files in this example contain the selected intervals. With no calibration provided, `leq_db_spl` is `None`.
