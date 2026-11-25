# Mission 4 — Dataset Data Card
**Team 06 | The Doorbell's Ears | EDGE_AI Module 2**

### 1. Dataset overview and source
The dataset consists of 144 audio clips supplied by the course professor for the assignment. It contains six classes: `on`, `off`, `go`, `stop`, `_silence`, and `_unknown`. The clips were processed using an ESP32-S3-based audio feature extraction pipeline.

### 2. Processing configuration
- Sampling frequency: 16,000 Hz
- Audio format: 16-bit signed integer (i16)
- Window size: 480 samples
- Hop size: 320 samples
- FFT size: 512
- Mel feature dimensions: 40
- Samples per input packet: 320
- Storage mode: None (features streamed to the host)

### 3. Dataset composition
The continuous experiment produced 7,194 feature frames, each containing 40 features. Of these, 142 frames crossed clip boundaries and were excluded from supervised training. The final dataset contains **7,052 labelled feature frames across all 144 clips**.

| Class | Frames |
|---|---:|
| `_silence` | 1,176 |
| `_unknown` | 1,176 |
| `go` | 1,176 |
| `off` | 1,176 |
| `on` | 1,172 |
| `stop` | 1,176 |
| **Total** | **7,052** |

Each retained frame contains its feature vector, class label, clip ID and original `first_sample` position.

### 4. Loss accounting and integrity
The experiment expected 7,200 packets containing 2,304,000 samples. Three packets (indices 10, 11 and 200) were deliberately skipped. The ESP32 reported three sequence gaps, zero input CRC errors and 2,303,040 received samples. Its sample timeline remained at 2,304,000, preserving original sample positions after the gaps.

Five feature frames were not generated relative to the continuous baseline because feature windows were invalidated around the gaps. Another 142 boundary-mixed frames were excluded during dataset construction.

The highest repeatedly confirmed passing transmission speed was **4.68359375×** on `/dev/cu.usbmodem114301`. An observed failure occurred at 4.6875×.

### 5. Known limitations and intended use
The dataset is limited to the 144 professor-provided clips and the tested processing configuration. The deliberate packet-loss experiment and speed tests were conducted on one USB serial port. The packet-gap timeline estimation assumes fixed-size 320-sample packets. The dataset has not been established as representative of all real-world acoustic environments.

It is intended for educational experimentation, feature analysis and keyword-classification model development. It should not be treated as a validated production dataset or used alone for safety-critical or security-critical door-access decisions.

### 6. Dataset files
- `mission4_final_dataset.npz` — compressed supervised dataset.
- `mission4_final_dataset.csv` — features and metadata in CSV format.
- Supporting packet-loss summaries, clip boundaries and experiment results are retained in the `results/` directory.
