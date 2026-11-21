# pyacdete.loudspeaker.single_tone_thd

```python
single_tone_thd(mic_samples, fs, f0, max_order=3)
```

Estimate the total harmonic distortion (THD) of a loudspeaker with a single tone as input.

## Parameters

<dl class="api-fields">
<dt id="param-mic-samples"><code>mic_samples</code><span class="type">array_like, shape (N,)</span></dt>
<dd><p>Finite real numeric samples from one microphone channel. The microphone collects the acoustic signal, and the ADC converts it to digital samples. Pass a steady portion of the recording containing at least one complete cycle of the test tone. If the test frequency falls between FFT bins, use at least four cycles.</p></dd>
<dt id="param-fs"><code>fs</code><span class="type">float</span></dt>
<dd><p>Positive finite sampling frequency of the microphone recording in Hz.</p></dd>
<dt id="param-f0"><code>f0</code><span class="type">float</span></dt>
<dd><p>Positive finite fundamental frequency of the generated test signal in Hz. For a single tone, this is the frequency of the sine wave.</p></dd>
<dt id="param-max-order"><code>max_order</code><span class="type">int, optional</span></dt>
<dd><p>Highest harmonic order in the initial THD estimate. The default is <code>3</code>, so the initial estimate uses the second and third harmonics where the sampling frequency permits. The minimum is <code>2</code>.</p></dd>
</dl>

## Returns

**result : dict**

The arrays contain one entry per harmonic order from 1 through `max_order_used`.

| Key | Type | Description |
|---|---|---|
| `harmonic_order` | ndarray of int, shape (K,) | Orders 1 through K, with K equal to `max_order_used`. Order 1 is the fundamental. |
| `frequency_hz` | ndarray of float, shape (K,) | Target frequencies of the returned orders in Hz. |
| `amplitude_peak` | ndarray of float, shape (K,) | Estimated peak amplitude of each component on the same scale as `mic_samples`. |
| `thd_percent` | float | Reported THD in percent, using orders 2 through K. |
| `thd_base_percent` | float | THD through the requested maximum order, limited to frequencies below Nyquist. |
| `thd_extended_percent` | float | THD through three times the requested maximum order, limited to frequencies below Nyquist. |
| `max_order_used` | int | Highest order included in the reported THD. |
| `max_order_checked` | int | Highest order evaluated in the extended estimate. |

## Notes

### Basic Knowledge

THD is used to measure the degree of nonlinearity of a system. The reason why the test needs a single tone as input is that a sinusoid contains energy at only one positive frequency (recall the Fourier transform of a sinusoid).

When a sinusoid is applied to a linear time-invariant system, complex exponentials can be used to show that no new frequency components are created in steady state. Nonlinear or time-varying systems can create new frequency components. In a single-tone test, THD measures the output components at integer multiples of the test frequency. [1]

For a highest included order $K$, define $A_k$ as the peak amplitude measured at $kf_0$ in the microphone recording. The function uses THD relative to the measured fundamental. [2]

$$\mathrm{THD}_{K}(\%)=100\,\frac{\sqrt{\sum_{k=2}^{K}A_k^2}}{A_1}.$$

The RMS amplitude of each sinusoidal component is $A_k/\sqrt{2}$. That common factor cancels in the ratio, so consistently measured RMS and peak amplitudes give the same THD.

Broadband signals can mask distortion because the input may already contain energy at frequencies where the system generates new components. Both contributions then appear together in the output spectrum. [1]

A cubic model $y=x+0.1x^3$ illustrates the suitability of a single tone as input. The code compares a single tone with a multitone signal spanning 500 Hz to 8 kHz. It measures the 3 kHz peak amplitude in the input, output and simulated nonlinear contribution $y-x$.

```python
import numpy as np

fs = 48_000
f0 = 1_000
t = np.arange(fs) / fs
tone = 0.6 * np.sin(2 * np.pi * f0 * t)
broadband = tone + sum(
    0.03 * np.sin(2 * np.pi * f * t)
    for f in range(500, 8_001, 500)
    if f != f0
)

def peak_at_3khz(samples):
    # The one-second recording gives a 1 Hz bin spacing.
    spectrum = np.fft.rfft(samples)
    return 2 * abs(spectrum[3 * f0]) / len(samples)

for label, x in (("single tone", tone), ("broadband", broadband)):
    y = x + 0.1 * x**3
    print(
        f"{label:11s}  input {peak_at_3khz(x):.5f}  "
        f"output {peak_at_3khz(y):.5f}  "
        f"nonlinear contribution {peak_at_3khz(y - x):.5f}"
    )
```

```text
single tone  input 0.00000  output 0.00540  nonlinear contribution 0.00540
broadband    input 0.03000  output 0.02611  nonlinear contribution 0.00389
```

In the single-tone case the output at 3 kHz reveals the third harmonic directly. In the broadband case the 3 kHz input component is larger than the generated contribution, and the output amplitude alone cannot isolate the distortion.

#### FFT amplitude estimation

The function removes the sample mean and estimates each harmonic amplitude from a one-sided FFT. With an integer number of fundamental cycles in the record, $f_0$ and its harmonics fall on FFT bins, so the function uses a rectangular window and reads those bins directly. Otherwise it applies a Blackman–Harris window to reduce spectral leakage, zero-pads to eight times the record length and interpolates the magnitude spectrum at the target frequencies. The off-bin method needs at least four cycles to keep each harmonic centre outside the main lobe of the adjacent harmonic. A longer recording helps resolve weak components and components close to Nyquist. [3, 5]

For either window, peak amplitudes are scaled by $2/\sum_n w[n]$, where $w[n]$ contains the window weights over the original samples. Only harmonics strictly below the Nyquist frequency $f_s/2$ are evaluated. Amplitudes at floating-point precision are set to zero. Broadband noise can still affect amplitude estimates at the frequencies being evaluated. [2, 4]

### Beyond Basic Definitions

Universal Audio describes how the number of harmonics to include in a THD calculation is related to the degree of nonlinearity. If the nonlinearity is mild, a small number of harmonics can account for most of the distortion. If it is more severe, more harmonics may be needed. [1]

The function computes THD twice from the same harmonic amplitudes and fundamental. The initial estimate uses up to `max_order`. The extended estimate checks up to `3 * max_order`. Each cutoff is limited to the highest order strictly below Nyquist. Adding orders to the same sum of squares can only keep the result the same or increase it. [2, 4]

```text
base_order = min(max_order, highest_order_below_nyquist)
checked_order = min(3 * max_order, highest_order_below_nyquist)
THD1 = THD through base_order
THD2 = THD through checked_order

small = min(THD1, THD2)
big = max(THD1, THD2)

if big - small > 0.10 * small:
    report THD2 and checked_order
    issue RuntimeWarning
else:
    report THD1 and base_order
```

The comparison uses a **10% relative tolerance** for this API. A rise of 10% means that the added orders account for about 17.4% of the harmonic power in the extended estimate. The rule also handles a zero initial estimate. Two zero estimates retain the initial cutoff, and a positive extended estimate selects the extended cutoff.

The warning indicates a material contribution from higher-order harmonics, which can indicate stronger nonlinear behavior under the test conditions. The tolerance is an implementation choice for selecting orders. It measures how much the added orders change the result. Device severity also depends on the absolute distortion level and the measurement conditions. [1, 2]

### Input checks and reproducibility

A `ValueError` is raised for invalid sample data or parameters, a recording shorter than the required number of cycles, a recording without a usable fundamental, or a test frequency for which the second harmonic is at or above Nyquist. Keep the test frequency, playback level, microphone position, sampling frequency and analyzed sample interval with each measurement.

## References

1. Universal Audio. [Total Harmonic Distortion](https://www.uaudio.com/blogs/ua/total-harmonic-distortion).
2. Audio Precision. [THD and THD+N – Similar, but Not the Same](https://www.audioprecision.com/blog/thd-and-thdn-similar-but-not-the-same).
3. National Instruments. [Understanding FFTs and Windowing](https://www.ni.com/en/shop/data-acquisition/measurement-fundamentals/analog-fundamentals/understanding-ffts-and-windowing.html).
4. MathWorks Signal Processing Toolbox reference. [thd](https://www.mathworks.com/help/signal/ref/thd.html).
5. SciPy reference. [Blackman–Harris window](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.windows.blackmanharris.html).
