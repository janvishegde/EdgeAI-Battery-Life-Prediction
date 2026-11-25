---
title: "Team 6 (Pixel) — Missions 1 and 2, from zero"
subtitle: "A step-by-step guide for a complete beginner. Nothing is assumed."
---

# 0. Read this first

**You are not dumb.** This looks scary only because it has many small steps. Each step below is tiny. Do them in order. Do not skip. After every step there is a box called **"You should see"**. If you see that, move on. If you do not, go to the box called **"If not"**, or send me a message with a screenshot.

**What is this whole thing?**
The doorbell company wants to know: can the doorbell *hear* properly? Your laptop pretends to be the microphone. Your small green board (the ESP32-S3) pretends to be the doorbell. Your laptop sends sound to the board through a USB cable. We measure two things:

- **Mission 1:** how fast can the sound go through the cable?
- **Mission 2:** how should we pack the sound (how many numbers per second, how big each number is), and where should the board keep it so it is not lost when unplugged?

**Words you will meet (simple meanings)**

| Word | Meaning |
|---|---|
| Terminal | A black or white window where you type commands and press Enter. Python programs are started from here. |
| Folder / directory | A place on your computer that holds files. |
| Port | The plug on the board (and the name your laptop gives it). Your board has two. |
| Upload | Copying our program from the laptop into the board. |
| Sketch | A program for the board. Arduino calls programs "sketches". |
| Baud | Speed setting of a serial cable. Bigger = faster (only for one of your two ports). |
| Bytes per second | How much data moves each second. 1 kB = 1000 bytes. |
| CRC | A checksum: a short code made from all the data. If two CRCs match, the data is identical. |
| RAM | Memory that forgets everything when power goes off. |
| Flash | Memory that keeps data even with no power (like a phone's storage). |

**Windows or Mac?** Both are explained. Ignore the one you don't use. On a Mac, wherever I write `python` you type `python3`, and wherever I write `pip` you type `pip3`.

**How to type commands:** I show commands in grey boxes. Type them exactly, then press **Enter**. Where you see `<COM-PORT>` or `<USB-PORT>`, delete the angle brackets and put your real port name (you will find it in Part 3).

**Keep a notebook.** Open a note on your phone or a paper page. You will write down numbers. There is a "numbers to write down" list in Part 9.

# Part 1. Install the software (about 30 minutes)

## 1A. Install Python

**Windows**

1. Open your browser and go to `python.org/downloads`. Click the big yellow **Download Python** button.
2. Open the file that downloads.
3. **Very important:** in the first window, at the bottom, tick the box **"Add python.exe to PATH"**. Then click **Install Now**.
4. Wait. Click **Close** when it says "Setup was successful".

**Mac**

1. Go to `python.org/downloads` and click the big yellow Download button.
2. Open the downloaded `.pkg` file and click **Continue** / **Agree** / **Install** until it finishes.

**You should see:** nothing special. We check in 1B.

## 1B. Open a terminal and check Python

**Windows:** press the **Windows key**, type `cmd`, press **Enter**. A black window opens. That is your terminal.
**Mac:** press **Cmd + Space**, type `Terminal`, press **Enter**. A window opens.

Type this and press Enter:

```
python --version
```
(Mac: `python3 --version`)

**You should see:** `Python 3.1x.x` (any number 3.10 or higher is fine).
**If not (Windows says "python is not recognized"):** you forgot the PATH tick. Run the Python installer again, choose **Modify**/**Repair**... simplest is to uninstall Python, install again, and tick the box this time.

## 1C. Install the Python helper packages

In the terminal type:

```
pip install numpy pyserial matplotlib
```
(Mac: `pip3 install numpy pyserial matplotlib`)

**You should see:** lots of text scrolling, ending with "Successfully installed ...". It can take a few minutes.
**If not:** if it says "pip is not recognized", try `python -m pip install numpy pyserial matplotlib` (Mac: `python3 -m pip install ...`).

## 1D. Install the Arduino IDE (the program that puts code into the board)

1. Go to `arduino.cc/en/software` and download **Arduino IDE 2.x** for your system.
2. Install it with the default choices. On Windows, if it asks to install drivers, click **Install** / **Yes**.
3. Open **Arduino IDE** from your Start menu / Applications.

## 1E. Add support for the ESP32 board (one-time)

Arduino does not know your board until you add it.

1. In Arduino IDE, look at the **left side**. There is a thin column of icons. Click the one that looks like **a board / chip** (its tooltip says **Boards Manager**).
2. In the search box type `esp32`.
3. Find the entry **"esp32 by Espressif Systems"**. Click **INSTALL**. Choose the newest **3.x** version (for example 3.0.x or 3.1.x or 3.2.x).
4. Wait. It downloads a lot (a few hundred MB). The bottom of the window shows progress. It finishes when the button says **REMOVE** and the text says INSTALLED.

**If not:** you need a working internet connection. If it stalls, close and reopen the IDE and try again.

## 1F. Unzip my folder

1. Find the file `team_06_module2_work.zip` that I sent. Save it on your **Desktop**.
2. **Windows:** right-click it → **Extract All...** → **Extract**.
   **Mac:** double-click it.
3. You now have a folder called `team_06_module2`. Open it. You should see files like `m1_pipe.py`, `m2_storage.py`, `board_link.py`, and a folder called `doorbell_board_starter`.

# Part 2. Open a terminal inside that folder

All Python commands must be run from inside `team_06_module2`. This is the most common mistake.

**Windows**

1. Open the `team_06_module2` folder in File Explorer.
2. Click once on the **address bar** at the top (where the folder path is shown).
3. Type `cmd` and press **Enter**. A black window opens already inside the folder.

**Mac**

1. Open **Terminal**.
2. Type `cd ` (the letters c, d, and then one space). Do not press Enter yet.
3. Drag the `team_06_module2` folder from Finder **into the Terminal window**. Its path appears.
4. Now press **Enter**.

**Check:** type `dir` (Windows) or `ls` (Mac) and press Enter.
**You should see:** a list that includes `m1_pipe.py`. If you don't, you are in the wrong folder; repeat Part 2.

Leave this terminal open. We will use it all day.

# Part 3. Plug in the board and find the two ports

## 3A. The board's two plugs

Look at the board. On one short edge there are **two USB-C sockets**. Next to them small letters say **COM** (or UART) and **USB**.

- The **COM** socket goes through a little translator chip. It behaves like an old serial cable, and its speed can be set (the baud).
- The **USB** socket is the chip's own direct USB. Its speed cannot be set.

This difference is the answer to a question in Mission 1, so remember it.

## 3B. Plug in both

Use **two USB cables** (data cables, not charge-only ones). Plug one cable from **COM** to the laptop and one from **USB** to the laptop. A small light on the board should come on.

**If no light:** try a different cable or port. Some cables only charge.

## 3C. Find the port names

In the terminal type:

```
python board_link.py ports
```
(Mac: `python3 board_link.py ports`)

**You should see:** a list of names with descriptions.

- **Windows** names look like `COM3`, `COM4`.
- **Mac** names look like `/dev/cu.usbserial-0001` and `/dev/cu.usbmodem1101`.

**Which is which?** Unplug the **COM** cable, wait 3 seconds, and run the command again. The name that **disappeared** is your COM port. Plug it back in. The other one is the USB port.

- On a Mac the COM one usually contains `usbserial`, `wchusbserial`, or `SLAB`, and the USB one contains `usbmodem`.

**Write down:** `COM-PORT = ______` and `USB-PORT = ______`.

**If a port is missing on Windows:** the COM chip may need a driver. Search the web for "CP210x driver" (or "CH340 driver" if your board has a CH340 chip) and install it, then replug.

# Part 4. Put the program into the board

## 4A. Open the sketch

1. In Arduino IDE click **File → Open...**
2. Go into `team_06_module2` → `doorbell_board_starter`. Click the file **doorbell_board_starter.ino**. Click **Open**.
3. Two tabs appear at the top: `doorbell_board_starter.ino` and `features.h`. Good, that is expected.

## 4B. Choose the board and the settings

Click the menu **Tools** at the top. You will change **six** things. A wrong setting here is the most common reason for later errors, so go slowly.

1. **Tools → Board → esp32 → ESP32S3 Dev Module.** (The list is long. Scroll.)
2. **Tools → USB CDC On Boot → Enabled.**
3. **Tools → Flash Size → 16MB (128Mb).**
4. **Tools → Partition Scheme → 16M Flash (3MB APP/9.9MB FATFS).**
5. **Tools → PSRAM → OPI PSRAM.** (Not "QSPI PSRAM", not "Disabled".)
6. **Tools → Port →** pick your **COM-PORT** from Part 3.

Leave every other setting as it is.

Why these? The board has 16 MB of flash and 8 MB of "octal" memory called PSRAM. Arduino assumes smaller defaults (4 MB flash, no PSRAM). With the wrong settings the 144 sound clips (4.6 MB) cannot be stored. Finding out *why* is part of Mission 2, so write down in your notebook: "default flash was 4MB, we changed to 16MB, default partition had about 1.5 MB for files, we changed to one with 9.9 MB, PSRAM was off/wrong type, we chose OPI".

**Check:** click the Tools menu again and make sure each of the six shows what you chose.

## 4C. Upload

1. Click the **right-pointing arrow button** near the top-left of the window (it is the **Upload** button). 
2. The first time, it compiles for a few minutes. The bottom panel (**Output**) shows text scrolling.
3. When the bottom shows something like **"Hard resetting via RTS pin..."** or "Leaving... " and no red text, it worked.

**If you see "Failed to connect to ESP32" / "Timed out waiting for packet header":**

1. Find the small button labelled **BOOT** on the board.
2. Click Upload again. When the Output shows "Connecting......", **press and hold BOOT**.
3. When the text moves on to "Writing at ...", you can let go.
4. When it finishes, press the small **RST** (reset) button once.

**If you see red text about the sketch being too big:** your Partition Scheme is wrong. Re-check step 4B number 4.
**If you see red errors about `LittleFS` or `Serial0`:** tell me the exact red text; send a screenshot.

## 4D. Close anything that uses the port

If you opened the Arduino **Serial Monitor** (magnifying glass at the top right), **close it**. Two programs cannot use one port. Python needs the port for itself. You can also close Arduino IDE now, but keep the board plugged in.

# Part 5. Check that the board answers

Type (using your real port names, without the angle brackets):

```
python board_link.py --port <COM-PORT> info
python board_link.py --port <USB-PORT> info
```
Example on Windows: `python board_link.py --port COM5 info`
Example on Mac: `python3 board_link.py --port /dev/cu.usbmodem1101 info`

**You should see** a list like this (numbers will differ):

```
cpu_mhz               240
heap_free         ~300,000
psram_size      ~8,000,000
flash_chip     16,777,216
fs_total       ~10,000,000
```

**Check these three:**

- `psram_size` should be about **8 million**. If it is **0**, PSRAM is not OPI. Fix Tools → PSRAM and upload again.
- `flash_chip` should be **16,777,216**. If it is 4,194,304, Flash Size is wrong. Fix and upload again.
- `fs_total` should be about **10 million**. If it is about 1.5 million, the Partition Scheme is wrong. Fix and upload again.

**If it says "no reply from the board" / times out:** press **RST**, check you used the right port, try the other port, and make sure the Arduino Serial Monitor is closed.

**Send me this output** before moving on, so I can check it with you.

# Part 6. Mission 1: how fast is the cable?

## 6A. Write your predictions first (3 minutes)

The assignment wants you to guess *before* measuring. The draft PDF already contains my predictions for Mission 1. Read that section. Also, as the assignment says, **ask any LLM**: "How many bytes per second can I send to an ESP32-S3 over USB?" and copy its answer into your notebook (it goes in the LLM log later). Later, check whether it was right.

## 6B. See the predictions on screen

```
python m1_pipe.py predict
```
**You should see:** tables of bytes per second, e.g. "16 kHz i16: 32,000 B/s".

## 6C. Measure the COM port at three baud rates

```
python m1_pipe.py com --port <COM-PORT>
```
This takes **a few minutes**, because 115,200 baud is slow. Do not touch anything. It tries three speeds and prints a line for each run.

**You should see** lines like:

```
com  baud=  115200 i16 16k spp=320  speed=0  run1:  11,3xx B/s (laptop) | board ms=... gaps=0 crc=0
```
The number before "B/s" is what you measured. Run 0 of each baud is a warm-up (slower); runs 1 to 3 are the real ones.

**If it says "board ... does not answer PING":** press RST on the board and run the command again.
**If it hangs forever:** close the terminal, open a new one (Part 2), unplug and replug the board, and try again.

## 6D. Measure the USB port

```
python m1_pipe.py usb --port <USB-PORT>
```
**You should see** a much bigger number than the COM rows at low baud (the USB port does not care about baud).

## 6E. Draw the graph

```
python m1_pipe.py plot
```
**You should see:** "wrote figs/m1_speed_vs_baud.png". Open that picture (in the `figs` folder). It is your speed-vs-baud plot for the report.

## 6F. "Can it keep up with real time?" table

This sends 5 seconds of sound at normal speed, five times, for different formats. Run it for each port you want to test:

```
python m1_pipe.py realtime --port <COM-PORT> --label com --baud 921600
python m1_pipe.py realtime --port <USB-PORT> --label usb
```
After each line it prints "CARRIES it" or "CANNOT keep up". Write each answer in your notebook. For the table in the report you want COM at 115,200, 921,600, and 2,000,000 baud, and USB. For another COM speed change the number after `--baud` (for example `--baud 115200`; it can take a few minutes).

## 6G. Packet size experiment

```
python m1_pipe.py packets --port <USB-PORT> --label usb
```
It sends the same sound in packets of 8, 64, 320 and 1,024 samples. **You should see** that tiny packets (8) are much slower than big ones.

## 6H. Features coming back

This one needs no board. It is already calculated: 50 frames per second × 181 bytes = **9,050 bytes per second**. Write it in your notebook.

# Part 7. Mission 2: where to keep the sound

The aliasing plot, the signal-to-noise numbers and the choice of format are already done. They are in the draft PDF. What is left is the board part: **storage**.

## 7A. How much does the board's fast memory hold?

```
python m2_storage.py sram --port <USB-PORT>
```
**You should see:** "largest SRAM store the board accepts: ... bytes" and a few lines saying how many seconds that is. Write the bytes in your notebook. Then it streams that much and prints "CRC board ... laptop ..." The two CRC values should be **identical**.

## 7B. Does the big PSRAM work?

```
python m2_storage.py psram --port <USB-PORT>
```
**You should see:** the 16 kHz float32 row says an **error** (it needs 9.2 MB, more than 8 MB), and the int16 and int8 rows say **OK**.
**If everything fails with "no psram":** go back to Part 4B (PSRAM must be OPI), upload again, then retry. The assignment says: do not edit any code until you know why. Write down what you found.

## 7C. Store all 144 clips, then save to flash

```
python m2_storage.py send --port <USB-PORT>
```
It sends all 144 clips (4,608,000 bytes), keeps them in PSRAM, copies them to flash, and prints the CRCs.

**You should see:** "payload 4,608,000 bytes, crc32 f702a9e3", then "save:" with `n: 4608000` and a CRC `f702a9e3`, and "flash CRC" `f702a9e3`. All three CRCs must be the same.

**If it says "ERR flash full":** your file system is too small. Check Part 4B number 3 and 4, upload again.

## 7D. The power-cut test

1. **Unplug both USB cables.** Wait 5 seconds.
2. Plug both back in. Wait 3 seconds.
3. Run:

```
python m2_storage.py check --port <USB-PORT>
```

**You should see:**

- `psram:` with `n: 0` (RAM forgot everything: that is correct and is the point of the test).
- `flash:` with the same `n: 4608000` and CRC `f702a9e3`.
- "identical to what was sent: True".

Write in your notebook: "PSRAM did not survive, flash did".

# Part 8. Put it in the report

1. Open the draft `team_06_missions_1_2_draft.pdf` (or the text version `missions_1_2.md`).
2. Everywhere it says **[BOARD: ...]**, type in the number you wrote in your notebook. Easiest: copy the whole text into a Google Doc or Word and edit there.
3. Add your own short sentences under **"What we learnt"** for both missions.
4. In **"LLM log"**: write what you asked an LLM (the USB speed question, plus this help from me), what it answered, and what you checked yourself. The assignment says hiding LLM use loses marks.
5. Save the final file as a **PDF**.

**Easiest of all:** copy the text from your terminal after each command and send it to me. I will fill the blanks for you and give you the finished PDF.

# Part 9. Numbers to write down (your notebook list)

**Setup**

- COM-PORT name: ______  USB-PORT name: ______
- `psram_size`: ______  `fs_total`: ______  `flash_chip`: ______

**Mission 1**

- COM speed at 115,200 baud: ______ B/s
- COM speed at 921,600 baud: ______ B/s
- COM speed at 2,000,000 baud: ______ B/s
- USB speed: ______ B/s
- Real-time table: for each of 16 kHz f32, 16 kHz i16, 16 kHz i8, 8 kHz i16, 8 kHz i8, did it CARRY or CANNOT on COM 115,200 / 921,600 / 2M and USB?
- Speed with 8, 64, 320, 1,024 samples per packet: ______ / ______ / ______ / ______
- Features coming back: 9,050 B/s (already done)

**Mission 2**

- Largest SRAM store: ______ bytes = ______ seconds at 16 kHz int16
- PSRAM: which rows said OK / error
- `SAVE` reply: n=______ us=______ crc=______
- Flash CRC after replug: ______ (must equal f702a9e3)
- PSRAM after replug: n=______ (expected 0)

# Part 10. When things go wrong

| What you see | What to do |
|---|---|
| `python` is not recognized | Reinstall Python and tick "Add python.exe to PATH" (Windows). On a Mac use `python3`. |
| `No module named serial` / `numpy` | Run the pip command from Part 1C again. |
| `can't open file 'm1_pipe.py'` | You are in the wrong folder. Redo Part 2. |
| No ports listed | Try the other cable / USB socket. Install the CP210x driver (Windows). |
| "Failed to connect" when uploading | Hold BOOT while it says "Connecting...". |
| `no reply from the board` | Press RST. Check port name. Close Arduino Serial Monitor. |
| "Access is denied" / "Resource busy" | Another program holds the port. Close Serial Monitor and other terminals using it. |
| `psram_size` is 0 | Tools → PSRAM → OPI PSRAM. Upload again. |
| `fs_total` is small / `ERR flash full` | Tools → Flash Size → 16MB and Partition Scheme → 16M Flash (3MB APP/9.9MB FATFS). Upload again. |
| Board restarts again and again | Look at the Serial Monitor message (open it at 921600 baud), then send it to me. |
| A result looks impossible | Good. That is what the assignment wants you to notice. Tell me the number and we will find out why. |

**Rule of this course:** when something fails, do not guess. Read the message, write it in your notebook, and send me a screenshot or paste the text. I will help you read it.
