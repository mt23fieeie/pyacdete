# pyacdete

Python Acoustic Device Testing — loudspeaker frequency response, harmonic distortion, delay, and sound pressure level.

## Documentation

The English API reference covers [H1 magnitude and phase](https://mt23fieeie.github.io/pyacdete/), [single-tone THD](https://mt23fieeie.github.io/pyacdete/single-tone-thd.html), [time-domain delay](docs/cross-correlation-delay.html), and [equivalent continuous sound pressure level](https://mt23fieeie.github.io/pyacdete/spl-leq.html). GitHub Pages should publish from the `main` branch, `/docs` folder.

## Install

```shell
python -m pip install "./python/pyacdete[smard]"
```

```python
from pyacdete.loudspeaker import cross_correlation_delay, h1_response, single_tone_thd, spl_leq
```

See the documentation for SMARD configuration 2000, the exact reference and microphone filenames, and the recorded result.

## Rebuild the reference

```shell
npm ci
npm run build
```

The build updates the HTML reference pages, the downloadable Python source, and the local KaTeX assets in `docs`.

## Acknowledgment and feedback

This website was built with assistance from ChatGPT. Its content has been reviewed by a human, but is not guaranteed to be free of errors. Please send feedback to 1220010941@student.must.edu.mo.
