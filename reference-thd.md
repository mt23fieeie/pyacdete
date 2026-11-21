# pyacdete.loudspeaker.single_tone_thd

```python
single_tone_thd(mic_samples, fs, f0, max_order=3)
```

Estimate the total harmonic distortion (THD) of a loudspeaker with a single tone as input.

## Parameters

<dl class="api-fields">
<dt id="param-mic-samples"><code>mic_samples</code><span class="type">array_like, shape (N,)</span></dt>
<dd><p>Finite real numeric samples from one microphone channel. The microphone collects the acoustic signal, and the ADC converts it to digital samples. Use a whole number of test-tone cycles so the test frequency falls on an FFT bin.</p></dd>
<dt id="param-fs"><code>fs</code><span class="type">float</span></dt>
<dd><p>Positive finite sampling frequency of the microphone recording in Hz.</p></dd>
<dt id="param-f0"><code>f0</code><span class="type">float</span></dt>
<dd><p>Positive finite fundamental frequency of the generated test signal in Hz. For a single tone, this is the frequency of the sine wave.</p></dd>
<dt id="param-max-order"><code>max_order</code><span class="type">int, optional</span></dt>
<dd><p>Highest harmonic order in the initial THD estimate. The default is <code>3</code>, so the initial estimate uses the second and third harmonics. The minimum is <code>2</code>.</p></dd>
</dl>

## Returns

**result : dict**

| Key | Type | Description |
|---|---|---|
| `thd_percent` | float | Reported THD in percent. |
| `amplitude_peak` | ndarray of float, shape (K,) | Peak amplitudes `[A1, A2, ..., AK]`, from the fundamental through the highest order used. |

The amplitudes use the units of `mic_samples`. For samples expressed in pascals the peaks are in pascals.

## Notes

### Basic Knowledge

THD is used to measure the degree of nonlinearity of a system. The reason why the test needs a single tone as input is that a sinusoid contains energy at only one positive frequency (recall the Fourier transform of a sinusoid).

When a sinusoid is applied to a linear time-invariant system, complex exponentials can be used to show that no new frequency components are created. Nonlinear or time-varying systems can create new frequency components. In a single-tone test, THD measures the output components at integer multiples of the test frequency. [1]

For a highest included order $K$, define $A_k$ as the peak amplitude measured at $kf_0$ in the microphone recording. The function uses THD relative to the measured fundamental. [2]

$$\mathrm{THD}_{K}(\%)=100\,\frac{\sqrt{\sum_{k=2}^{K}A_k^2}}{A_1}.$$

The RMS amplitude of each sinusoidal component is $A_k/\sqrt{2}$. That common factor cancels in the ratio, so RMS and peak amplitudes give the same THD.

Broadband signals can mask distortion because the input may already contain energy at frequencies where the system generates new components. Both contributions then appear together in the output spectrum. [1]

A cubic model $y=x+0.1x^3$ illustrates this with a broadband input made of tones from 500 Hz to 8 kHz. The code measures the 3 kHz peak amplitude in the input, output and simulated nonlinear contribution $0.1x^3$.

```python
import numpy as np

fs = 48_000
n = fs  # 1 second
t = np.arange(n) / fs

input_signal = np.zeros(n)
for frequency in range(500, 8_001, 500):
    input_signal += 0.1 * np.cos(2 * np.pi * frequency * t)

generated_signal = 0.1 * input_signal**3
output_signal = input_signal + generated_signal

def peak_at_3khz(samples):
    bin_spacing = fs / len(samples)
    bin_3khz = round(3_000 / bin_spacing)
    spectrum = np.fft.rfft(samples)
    return 2 * abs(spectrum[bin_3khz]) / len(samples)

print(f"Input at 3 kHz = {peak_at_3khz(input_signal):.6f}")
print(f"Output at 3 kHz = {peak_at_3khz(output_signal):.6f}")
print(f"Generated component at 3 kHz = {peak_at_3khz(generated_signal):.6f}")
```

```text
Input at 3 kHz = 0.100000
Output at 3 kHz = 0.117575
Generated component at 3 kHz = 0.017575
```

The existing 3 kHz component and the generated component appear in the same output bin. The simulation computes the generated component directly as $0.1x^3$.

#### FFT amplitude estimation

The FFT bin spacing is $f_s/N$, where $N$ is the number of samples. With a whole number of fundamental cycles, $f_0$ and its harmonics fall on FFT bins. The function reads those bins directly and multiplies their magnitudes by $2/N$ to estimate peak amplitudes. [3, 4]

### Beyond Basic Definitions

Universal Audio describes how the number of harmonics to include in a THD calculation is related to the degree of nonlinearity. If the nonlinearity is mild, a small number of harmonics can account for most of the distortion. If it is more severe, more harmonics may be needed. [1]

The function computes THD twice from the same harmonic amplitudes and fundamental. The initial estimate uses orders up to `max_order`. The extended estimate uses orders up to `3 * max_order`.

```text
THD1 = THD through max_order
THD2 = THD through 3 * max_order

small = min(THD1, THD2)
big = max(THD1, THD2)

if big > 1.10 * small:
    issue RuntimeWarning
    return THD2 and its peak amplitudes
else:
    return THD1 and its peak amplitudes
```

The comparison uses a **10% relative tolerance** for this API. The rule also handles a zero initial estimate. Two zero estimates retain the initial cutoff, and a positive extended estimate selects the extended cutoff.

The warning indicates a material contribution from higher-order harmonics, which can indicate stronger nonlinear behavior under the test conditions. [1, 2] The tolerance of `0.1` is a tentative, illustrative value with no specific basis.

## References

1. Universal Audio. [Total Harmonic Distortion](https://www.uaudio.com/blogs/ua/total-harmonic-distortion).
2. Audio Precision. [THD and THD+N – Similar, but Not the Same](https://www.audioprecision.com/blog/thd-and-thdn-similar-but-not-the-same).
3. National Instruments. [Understanding FFTs and Windowing](https://www.ni.com/en/shop/data-acquisition/measurement-fundamentals/analog-fundamentals/understanding-ffts-and-windowing.html).
4. MathWorks MATLAB reference. [fft](https://www.mathworks.com/help/matlab/ref/fft.html).
