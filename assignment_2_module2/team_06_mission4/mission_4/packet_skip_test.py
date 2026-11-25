"""
Mission 4: Physical ESP32 packet-skip experiment.

Run locally on the Mac connected to the ESP32-S3.
Do not run this from GitHub Codespaces for USB serial access.
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

# Reuse the team's existing Mission 3 implementation.
MODULE3 = Path(__file__).resolve().parents[2] / "team_06_module3"
sys.path.insert(0, str(MODULE3))

from board_link import Board
from team_audio import get_clip

FS = 16000
WIN = 480
HOP = 320
NFFT = 512
MELS = 40
PACKET_SIZE = 320
TEAM = 6

# Deliberately omit these input packet sequence numbers.
SKIP_PACKETS = (10, 11, 20)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True, help="ESP32 serial port")
    parser.add_argument("--baud", type=int, default=921600)
    args = parser.parse_args()

    # Generate one labelled Team 6 audio clip.
    audio = get_clip(TEAM, clip_id=0, fs=FS)
    payload = np.round(
        np.clip(audio, -1.0, 1.0) * 32767
    ).astype("<i2").tobytes()

    total_samples = len(audio)
    expected_packets = (total_samples + PACKET_SIZE - 1) // PACKET_SIZE

    print("\nMISSION 4: PHYSICAL PACKET SKIP TEST")
    print("------------------------------------")
    print(f"Team: {TEAM}")
    print(f"Clip: 0")
    print(f"Label: on")
    print(f"Samples: {total_samples}")
    print(f"Input packets: {expected_packets}")
    print(f"Skipped packets: {SKIP_PACKETS}")
    print(f"Serial port: {args.port}")

    board = None

    try:
        board = Board(args.port, args.baud)

        if not board.ping():
            raise RuntimeError("ESP32 did not respond to PING")

        print("\nESP32 connection: OK")
        print("Streaming audio...")

        result = board.stream(
            payload,
            fs=FS,
            fmt="i16",
            win=WIN,
            hop=HOP,
            nfft=NFFT,
            mels=MELS,
            feat=True,
            store="none",
            speed=0,
            samples_per_packet=PACKET_SIZE,
            skip=SKIP_PACKETS,
        )

        report = {
            "experiment": "mission_4_packet_skip",
            "team": TEAM,
            "clip_id": 0,
            "label": "on",
            "sampling_rate": FS,
            "window": WIN,
            "hop": HOP,
            "samples_per_packet": PACKET_SIZE,
            "total_samples": total_samples,
            "expected_input_packets": expected_packets,
            "deliberately_skipped_packets": list(SKIP_PACKETS),
            "packets_sent": result["packets_sent"],
            "expected_feature_frames": result["expected_features"],
            "received_feature_frames": len(result["frame_numbers"]),
            "missing_feature_frames": result["lost_features"],
            "output_crc_errors": result["bad_crc_back"],
            "board_summary": result["board"],
            "board_ready": result["ready"],
        }

        print("\nEXPERIMENT RESULTS")
        print(json.dumps(report, indent=4))

        output = Path(__file__).resolve().parents[1] / "results"
        output.mkdir(parents=True, exist_ok=True)

        report_path = output / "packet_skip_test.json"
        with report_path.open("w", encoding="utf-8") as f:
            json.dump(report, f, indent=4)

        print(f"\nSaved report: {report_path}")

    finally:
        if board is not None:
            board.close()
            print("Serial connection closed.")


if __name__ == "__main__":
    main()
