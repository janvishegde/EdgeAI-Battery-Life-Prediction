# Team 6 (Pixel) — handover: Missions 1 and 2 are DONE, Missions 3, 4, 5 are left

Deadline: Monday 30 November 2026. Hand in one folder `team_06_module2/` as a zip (PDF of 5 mission records, all Python code,
finished sketch `.ino` + `features.h` with the Tools settings, the dataset, the data card, the commitment memo, LLM log and team reflection).

## What is in this folder
| File | What it is |
|---|---|
| `team_06_missions_1_2.pdf` (and `missions_1_2.md`, its source) | Mission records 1 and 2 with every measured number. Still to write by hand: the "What we learnt" parts and the first LLM question (marked **[YOUR WORDS]**) |
| `measurements_log.txt` | The raw terminal output behind every number (proof) |
| `m1_pipe.py` | Mission 1 measurements (`com`, `usb`, `realtime`, `packets`, `sweep`) |
| `m2_storage.py` | Mission 2 board tests (`info`, `sram`, `psram`, `send`, `check`) |
| `m2_analysis.py`, `quant.py` | Aliasing spectra, SQNR, quantise/pack/unpack |
| `make_m1_figure.py`, `figs/` | The graphs |
| `doorbell_board_starter/` | The board sketch. `SAVE` is finished. `features.h` is still the slow starter (Mission 3 job) |
| `board_link.py`, `team_audio.py`, `speech_pool.npz` | From the instructor. Do not edit |
| `ASSIGNMENT_README.md`, `TEAMS.csv` | The professor's original README (all five missions) and team list |
| `MISSION3_PROMPT_FOR_AI.txt` | A ready prompt to paste into an AI chat to be guided through Mission 3 |
| `BEGINNER_GUIDE.md` / `Team6_Beginner_Guide_Missions_1_2.pdf` | Step-by-step setup guide (Windows and Mac) |

## Settings that matter (Arduino IDE Tools menu)
Board ESP32S3 Dev Module · USB CDC On Boot Enabled · Flash Size 16MB (128Mb) · Partition Scheme "16M Flash (3MB APP/9.9MB FATFS)" ·
PSRAM OPI PSRAM · Upload Mode UART0 / Hardware CDC · Port = the COM socket. Everything else default.
The board already has the finished sketch uploaded. `info` should show psram_size 8,388,608 and fs_total 10,354,688.

## Decisions already made (chosen stream)
16 kHz, anti-alias filter on, int16, scale S = 1.0 (fixed, the doorbell cannot know the peak in advance). 144 clips = 4,608,000 bytes,
CRC32 `f702a9e3`. PSRAM = working copy, flash = saved copy. Features: win 480, hop 320, nfft 512, 40 mel (181 bytes per frame, 9,050 B/s back).

## Things we learnt the hard way
1. Port numbers (COM3, COM10 ...) differ on every laptop. `python board_link.py ports`; unplug one cable to see which name disappears.
2. The board keeps the baud rate you set. After a COM baud test press **RST** (the newer `m1_pipe.py` finds the rate itself).
3. USB port at `speed=0` LOSES data (about 190,000 B/s is the zero-loss limit; COM at 2,000,000 baud about 185,000). A speed measured with
   gaps or bad CRC is not a real speed. Use `python m1_pipe.py sweep --port <USB port> --label usb`. Cause is our hypothesis (board reads too slowly), not tested: Mission 4 can test it.
4. Close the Arduino Serial Monitor before running Python (one program per port).
5. We only have one cable: COM socket for upload and most tests, move it to the USB socket for USB tests.

## What is left
- **Mission 3** (features on the board): ask an LLM "how long does a 512-point FFT take on an ESP32-S3?" and log the answer first. Write `features()` in NumPy, plot log-mel of one clip per class, stream with features on at `speed=1` and read `compute_us` and `lag_s`, then make `features.h` faster (starter `dft()` calls `cosf`/`sinf` for every output; hints: twiddle table, radix-2 FFT). Every output within 0.05 dB of NumPy.
- **Mission 4** (nothing lost): loss accounting, `skip=(10, 11, 200)`, make a lost packet unable to shift labels, labelled dataset `.npz`, data card.
- **Mission 5** (laptop vs board): feature differences, nearest-centroid classifier, choose the setting to ship.
- Commitment memo, LLM log, team reflection (who held which role in each mission), final zip.
- Course rule: LLM for explanations and hints, not finished code; everyone must be able to explain every line; keep an honest LLM log.
