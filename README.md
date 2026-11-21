# pyacdete

Python Acoustic Device Testing for loudspeaker frequency response, harmonic distortion and delay estimation.

## Documentation

The English API reference covers H1 magnitude and phase, single-tone THD and time-domain delay estimation. GitHub Pages publishes the `/docs` folder on `main`. [API reference](https://mt23fieeie.github.io/pyacdete/) · [Delay example and reference source](reference-delay.md)

## Install

```shell
python -m pip install "./python/pyacdete[smard]"
```

```python
from pyacdete.loudspeaker import estimate_delay, h1_response, single_tone_thd
```

See the documentation for SMARD configuration 2000, the exact reference and microphone filenames, and the recorded result.

## Rebuild the reference

```shell
npm ci
npm run build
```

The build updates the HTML reference pages, the downloadable Python source, and the local KaTeX assets in `docs`.

## Acknowledgment and feedback

This website was built with assistance from ChatGPT. The H1 reference has been reviewed by a human. Please send feedback to 1220010941@student.must.edu.mo.
