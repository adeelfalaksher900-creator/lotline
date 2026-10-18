# Demonstration production

The final video is a 133-second, 1920×1080, 30fps Hyperframes composition built around actual browser interactions with the working application. The app recording uses a 1920×924 viewport with reserved brand and caption rails in the final frame.

It uses the real React frontend, FastAPI API, FalkorDBLite engine and Workers AI planner. The recorded flow covers one-hop and full-chain scope, repack/rework, shipment paths and source records, unverified stock, the query trace, exact hold review, approval, the decision receipt and an unknown lot.

Narration is a synthetic ElevenLabs library voice. It is not a recording or clone of Adeel's voice. Visible labels identify synthetic narration and fictional data. Captions derive from the voice's word timestamps. No product UI or results were reconstructed for the video.

Waiting time in the unknown-lot request is shortened, and the actual result is held for reading. The video is labelled as an edited sandbox demonstration. It makes no latency claim.

The Hyperframes source uses local Manrope and IBM Plex Mono fonts, a paused GSAP timeline and separate narration audio. All media timing is deterministic. The root DESIGN.md owns its palette.

## Reproduce

Use the application's documented local setup. The demo recording script drives actual UI interactions; it does not intercept or mock API responses. The Hyperframes wrapper expects its actual tour MP4 and the existing narrated audio alongside the composition. The generated media is distributed separately from app source.

```bash
cd media/demo
python3 assets/build-composition.py
HYPERFRAMES_BROWSER_PATH=/path/to/chromium npm run check
HYPERFRAMES_BROWSER_PATH=/path/to/chromium npm run render -- --fps 30 --quality high --workers 2 --output ../output/Lotline_Demo_1080p.mp4
```

The final composition check reported zero runtime or layout errors and 45 passing contrast checks. Two non-blocking maintainability warnings concern the chapter-label tracks in this single continuous scene. The authored source, check report and recording step log are kept with the production files. This documentation does not claim an external penetration test or a production benchmark.
