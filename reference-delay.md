# pyacdete.loudspeaker.cross_correlation_delay

```python
cross_correlation_delay(x, y, fs)
```

Estimate the **loopback-to-microphone delay** using time-domain cross-correlation. In a loudspeaker measurement, this delay includes sound propagation through air and can reflect delays introduced by the loudspeaker, the microphone, and the relative timing of the acquisition channels.

- Smaart’s Delay Finder “calculates the difference in time between your measurement signal and your reference signal” and lists “Propagation time from speaker to microphone” as a contributor. [1]
- Room EQ Wizard states that “measurements will be relative to the loopback timing” and identifies “the time it takes sound to travel from the speaker being measured to the microphone” as part of the measured delay. [2]

## Parameters

<dl class="api-fields">
<dt id="param-x"><code>x</code><span class="type">array_like, shape (N,)</span></dt>
<dd><p>Real, one-dimensional samples of the synchronously recorded electrical loopback reference.</p></dd>
<dt id="param-y"><code>y</code><span class="type">array_like, shape (N,)</span></dt>
<dd><p>Real, one-dimensional samples of the corresponding microphone recording. Use the same length, sampling rate, and recording window as <code>x</code>. Sample zero represents the same acquisition instant in both arrays, preserving the delay between the recorded waveforms.</p></dd>
<dt id="param-fs"><code>fs</code><span class="type">float</span></dt>
<dd><p>Positive finite sampling frequency shared by both recordings, in Hz.</p></dd>
</dl>

Both arrays must be nonempty, contain only finite samples, and have a varying signal.

## Returns

**result : dict**

| Key | Type | Description |
|---|---|---|
| `delay_samples` | int | Signed integer sample lag. A positive value means `y` is delayed relative to `x`. A negative value means `y` leads `x`. |
| `delay_seconds` | float | `delay_samples / fs`, in seconds. |

## Notes

### 1. General idea

In the conventional two-microphone model, two signals $x_1(t)$ and $x_2(t)$ come from a single source $s(t)$. The second signal contains a scaled, delayed copy of the source. The terms $n_1(t)$ and $n_2(t)$ represent noise. [3]

$$
\begin{aligned}
x_1(t) &= s(t) + n_1(t), \\
x_2(t) &= a\,s(t-D) + n_2(t).
\end{aligned}
$$

Hold one signal fixed and shift the other along the time axis. The shift that maximizes their similarity estimates the delay. In this API, the two observed signals are the electrical loopback and the microphone recording.

### 2. Cross-correlation and delay

Subtract the mean from each signal. For the resulting discrete signals, find the peak of the full linear cross-correlation and convert its lag from samples to seconds. [3, 4, 5]

$$
C_{12}[k] = \sum_n x_1[n]x_2[n+k],
\qquad \widehat{k} = \arg\max_k C_{12}[k],
\qquad \widehat{D} = \frac{\widehat{k}}{f_s}.
$$

For real-valued inputs, this convention matches `correlate(y, x, mode="full")`. A positive lag means the microphone recording arrives after the reference. SciPy’s `method="auto"` selects direct summation or FFT computation for the same linear cross-correlation. [4]

At $f_s=8000\,\mathrm{Hz}$, a lag of 25 samples corresponds to

$$
\widehat{D} = \frac{25}{8000}\,\mathrm{s}
= 0.003125\,\mathrm{s}
= 3.125\,\mathrm{ms}.
$$

### 3. Limitations

- **Bandwidth.** A broad autocorrelation tends to produce a broad cross-correlation peak, making its location harder to estimate.
- **Finite observation time and noise.** Short recordings or strong noise can reduce the accuracy of the delay estimate.
- **Multipath propagation.** Direct sound and reflections can produce several peaks. The strongest peak can correspond to a reflected path.

## References

1. Rational Acoustics. [Delay Finder vs. Delay Tracker](https://support.rationalacoustics.com/support/solutions/articles/150000184350-delay-finder-vs-delay-tracker).
2. Room EQ Wizard. [Making Measurements](https://www.roomeqwizard.com/betahelp/help/html/makingmeasurements.html).
3. C. H. Knapp and G. C. Carter. [The generalized correlation method for estimation of time delay](https://doi.org/10.1109/TASSP.1976.1162830). *IEEE Transactions on Acoustics, Speech, and Signal Processing*, 24(4), 320–327, 1976.
4. SciPy. [`scipy.signal.correlate`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlate.html).
5. SciPy. [`scipy.signal.correlation_lags`](https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.correlation_lags.html).
