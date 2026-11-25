# pyacdete.loudspeaker.spl_leq

```python
spl_leq(mic_samples, fs, *, calibration=None)
```

Compute the RMS level of a selected mono microphone recording. When calibration is supplied, estimate the unweighted equivalent continuous sound pressure level $L_{\mathrm{eq}}$ from the ratio of the test and calibration RMS amplitudes.

## Parameters

<dl class="api-fields">
<dt id="param-mic-samples"><code>mic_samples</code><span class="type">array_like, shape (N,)</span></dt>
<dd><p>Nonempty, finite real samples from one microphone channel over the interval to analyze.</p></dd>
<dt id="param-fs"><code>fs</code><span class="type">float</span></dt>
<dd><p>Positive, finite sampling frequency of <code>mic_samples</code>, in Hz.</p></dd>
<dt id="param-calibration"><code>calibration</code><span class="type">tuple (array_like, float) or None, optional</span></dt>
<dd><p>Pair <code>(cal_samples, level_db_spl)</code>. <code>cal_samples</code> contains mono calibration samples recorded through the same microphone chain. <code>level_db_spl</code> is the known calibration level in dB SPL. The default is <code>None</code>.</p></dd>
</dl>

## Returns

**result : dict**

| Key | Type | Description |
|---|---|---|
| `duration_s` | float | Duration of the selected interval in seconds, calculated as `len(mic_samples) / fs`. |
| `rms` | float | Root-mean-square amplitude of `mic_samples`, in the same units as the input samples. |
| `leq_db_spl` | float or `None` | Unweighted equivalent continuous sound pressure level in dB SPL. Returns `None` when calibration is omitted and `-inf` when valid calibration is supplied and the test RMS is zero. |

## Notes

### Basic Concepts and Theoretical Derivation of SPL Formula

Sound produces pressure fluctuations around the ambient air pressure at the microphone. Sound pressure level (SPL) compares the root-mean-square (RMS) size of those fluctuations with a reference pressure on a decibel scale.

**Notation**

The subscript $\mathrm{cal}$ denotes the calibration segment or a quantity associated with it. In each test–calibration pair, the symbol without $\mathrm{cal}$ refers to the test segment.

| Symbol | Definition |
|---|---|
| $p(t),\,p(t_n),\,p_s(t)$ | Instantaneous sound pressure in Pa, its value at the $n$th sampling instant $t_n$, and the pressure waveform selected for analysis. Here $p_s(t)=p(t)$. |
| $(\cdot)_{\mathrm{av}},\,P_{\mathrm{RMS}},\,P_{\mathrm{cal}}$ | Time averaging over the selected segment and the RMS sound pressures in Pa. For the test segment, $P_{\mathrm{RMS}}=\sqrt{(p_s^2)_{\mathrm{av}}}$. |
| $L_{\mathrm{cal}},\,P_{\mathrm{REF}}$ | Given quantities. $L_{\mathrm{cal}}$ is the known sound pressure level of the calibrator, for example 94 dB SPL. $P_{\mathrm{REF}}=20\,\mu\mathrm{Pa}$ is the reference sound pressure in air. |
| $L_p$ | Sound pressure level of the test segment, in dB relative to $P_{\mathrm{REF}}$. |
| $x(t),\,x(n),\,x_{\mathrm{cal}}(n)$ | Continuous-time representation of the normalized test signal and dimensionless sample sequences for the test and calibration segments. |
| $N,\,N_{\mathrm{cal}},\,T_s,\,T$ | Sample counts, sampling interval, and test-window duration, with $T=NT_s$. |
| $X_{\mathrm{ef}},\,X_{\mathrm{cal}}$ | Digital RMS amplitudes of the two segments. |
| $K$ | Positive conversion factor from sound pressure to normalized digital amplitude, in $\mathrm{Pa}^{-1}$. |

**Derivation**

Assume both recordings use the same acquisition chain.

We will employ these equalities from two references.

**Pierce (2019)**

$$
L_p = 10\log_{10}\!\left(\frac{(p_s^2)_{\mathrm{av}}}{P_{\mathrm{REF}}^2}\right).
\tag{2.3.1}
$$

**Miyara (2017)**

$$
\begin{aligned}
X_{\mathrm{ef}} &= \sqrt{\frac{1}{N}\sum_{n=1}^{N}x^2(n)} && (7.2)\\
x(n) &= Kp(t_n) && (7.3)\\
X_{\mathrm{cal}} &= \sqrt{\frac{1}{N_{\mathrm{cal}}}\sum_{n=1}^{N_{\mathrm{cal}}}x_{\mathrm{cal}}^2(n)} && (7.4)\\
P_{\mathrm{cal}} &= P_{\mathrm{REF}}10^{L_{\mathrm{cal}}/20} && (7.5)\\
K &= \frac{X_{\mathrm{cal}}}{P_{\mathrm{REF}}10^{L_{\mathrm{cal}}/20}} && (7.6)
\end{aligned}
$$

From Pierce's SPL definition,

$$
\begin{aligned}
L_p
&\overset{(2.3.1)}{=}10\log_{10}\!\left(\frac{(p_s^2)_{\mathrm{av}}}{P_{\mathrm{REF}}^2}\right)\\
&\overset{\text{RMS definition}}{=}10\log_{10}\!\left[\left(\frac{P_{\mathrm{RMS}}}{P_{\mathrm{REF}}}\right)^2\right]\\
&\overset{\text{log power rule}}{=}20\log_{10}\!\left(\frac{P_{\mathrm{RMS}}}{P_{\mathrm{REF}}}\right).
\end{aligned}
$$

Square Miyara's continuous RMS expression (7.1) and approximate the integral using equally spaced samples.

$$
\begin{aligned}
\frac{1}{T}\int_0^T x^2(t)\,\mathrm{d}t
&\overset{\text{uniform sampling}}{\simeq}\frac{T_s}{T}\sum_{n=1}^{N}x^2(n)\\
&\overset{T=NT_s}{=}\frac{1}{N}\sum_{n=1}^{N}x^2(n)
\overset{(7.2)}{=}X_{\mathrm{ef}}^2,\\
X_{\mathrm{cal}}^2
&\overset{(7.4)}{=}\frac{1}{N_{\mathrm{cal}}}\sum_{n=1}^{N_{\mathrm{cal}}}x_{\mathrm{cal}}^2(n).
\end{aligned}
$$

For the remaining steps, use sampled RMS values. In our measurements, sound pressure is the input to the microphone transducer, and the acquisition chain records its output as dimensionless digital samples. We assume the following relation between the input pressure and the recorded samples, with conversion factor $K$.

$$
\begin{aligned}
x(n)&\overset{(7.3)}{=}Kp(t_n),\\
X_{\mathrm{ef}}&\overset{\text{take RMS},\,K>0}{=}KP_{\mathrm{RMS}},\\
X_{\mathrm{cal}}&\overset{\text{take RMS, same }K}{=}KP_{\mathrm{cal}}.
\end{aligned}
$$

Apply Pierce's inverse relation (2.3.2) to the known calibration level and solve for $K$.

$$
\begin{aligned}
P_{\mathrm{cal}}&\overset{(7.5)}{=}P_{\mathrm{REF}}10^{L_{\mathrm{cal}}/20},\\
K&\overset{(7.6)}{=}\frac{X_{\mathrm{cal}}}{P_{\mathrm{cal}}}.
\end{aligned}
$$

Substituting into the SPL definition gives Miyara's Eq. (7.7).

$$
\begin{aligned}
L_p
&\overset{P_{\mathrm{RMS}}=X_{\mathrm{ef}}/K}{=}
20\log_{10}\!\left(\frac{X_{\mathrm{ef}}/K}{P_{\mathrm{REF}}}\right)\\
&\overset{(7.6)}{=}
20\log_{10}\!\left(\frac{X_{\mathrm{ef}}}{X_{\mathrm{cal}}}
\frac{P_{\mathrm{cal}}}{P_{\mathrm{REF}}}\right)\\
&\overset{\text{(7.5) and log product rule}}{=}
\boxed{L_{\mathrm{cal}}+20\log_{10}\!\left(\frac{X_{\mathrm{ef}}}{X_{\mathrm{cal}}}\right)}\\
&\overset{\text{log quotient rule}}{=}
20\log_{10}X_{\mathrm{ef}}-20\log_{10}X_{\mathrm{cal}}+L_{\mathrm{cal}}.
\end{aligned}
\tag{7.7}
$$

[Pierce (2019), §2.3.1](https://link.springer.com/chapter/10.1007/978-3-030-11214-1_2) · [Miyara (2017), §§7.3–7.4](https://link.springer.com/chapter/10.1007/978-3-319-55871-4_7)

## Examples

### Measure the SPL of a Yamaha MSR400 loudspeaker

Use the full 25 s microphone recording of a Yamaha MSR400 playing a STIPA test signal at position 2, measurement 1. The accompanying recording supplies the 1 kHz calibration tone at 94 dB SPL. Both WAV files are mono and sampled at 48 kHz. [Šimon Cieslar (2025), §9.2](https://www.vut.cz/en/students/final-thesis/detail/167229).

| File | Purpose |
|---|---|
| <a href="downloads/spl_leq_example.zip" download><code>spl_leq_example.zip</code></a> | Standalone function, example script, and installation requirements. |
| <a href="downloads/pyacdete-0.1.3-py3-none-any.whl" download><code>pyacdete-0.1.3-py3-none-any.whl</code></a> | Optional library package for importing the function in your own project. |
| [STIPA_MES1_P2.wav](https://raw.githubusercontent.com/Cieslar-Simon/STI/1b4a0c33740c52d62b81aad7b667b1f85c522fec/control_measurements/Position%202/STIPA_MES1_P2.wav) | Test recording (`mic_samples`). |
| [Reference_calibration_94_dB_SPL.wav](https://raw.githubusercontent.com/Cieslar-Simon/STI/1b4a0c33740c52d62b81aad7b667b1f85c522fec/control_measurements/Reference_calibration_94_dB_SPL.wav) | Calibration recording (`cal_samples`). |

#### Run the example in PowerShell

Extract the ZIP and open PowerShell in the folder containing `requirements.txt`. The script reads the WAV files from that folder if present, or downloads them automatically.

```powershell
py -m venv .venv
& ".\.venv\Scripts\python.exe" -m pip install --index-url https://pypi.org/simple --timeout 60 -r .\requirements.txt
& ".\.venv\Scripts\python.exe" .\sti_spl_example.py
```

To make the same measurement with the installed library, pass both recordings and the known calibration level.

```python
from pyacdete.loudspeaker import spl_leq

result = spl_leq(mic_samples, fs, calibration=(cal_samples, 94.0))
```

#### Recorded result

```text
Yamaha MSR400 | STIPA, Position 2, Measurement 1
Test segment: 25.000 s at 48000 Hz
Calibration: 1 kHz, 94.0 dB SPL
Test RMS: 0.0254437465
Calibration RMS: 0.3368177544
Unweighted Leq: 71.5637 dB SPL
```
