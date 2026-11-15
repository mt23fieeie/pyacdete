# Python Acoustic Device Testing

Install from this directory with `python -m pip install '.[smard]'`.

```python
from pyacdete.loudspeaker import h1_response
result = h1_response(x, y, fs, mode="both", threshold=0.9)
```

`x` and `y` are synchronized real one-dimensional reference and microphone
signals. The function plots coherence and the requested magnitude/phase
responses, exports CSV, and returns a dictionary of arrays. Close the plot
window to return. Set `save_path=None` to skip CSV export.

The H1 calculation core is copied unchanged from Yang's demo-aligned
`h1_api.py`. The package adds the `pyacdete.loudspeaker` import namespace.
No delay removal, channel normalization, smoothing, or resampling is applied.

Run `examples/test_smard.py` with the working directory set to the folder
containing `wgn_48kHz_ch8_DirLS.flac` and
`wgn_48kHz_ch24_single_mic.flac`.

The SMARD example estimates the reference-to-microphone measurement path.
Digital transfer magnitude is not dB SPL or an absolute sensitivity calibration.
