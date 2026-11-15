# pyacdete

Python Acoustic Device Testing — H1 loudspeaker magnitude and phase API.

## Documentation

The English API reference is in `docs/index.html`. GitHub Pages should publish from the `main` branch, `/docs` folder.

## Install

```shell
python -m pip install "./python/pyacdete[smard]"
```

```python
from pyacdete.loudspeaker import h1_response
```

See the documentation for SMARD configuration 2000, the exact reference and microphone filenames, and the recorded result.

## Rebuild the reference

```shell
npm ci
npm run build
```

The build updates `docs/index.html` and its local KaTeX assets. The remaining static assets and downloads are also stored in `docs`.

## Acknowledgment and feedback

This website was built with assistance from ChatGPT. Its content has been reviewed by a human, but is not guaranteed to be free of errors. Please send feedback to 1220010941@student.must.edu.mo.
