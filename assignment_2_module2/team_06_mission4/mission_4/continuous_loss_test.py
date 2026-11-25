
import argparse
import csv
import json
import sys
from pathlib import Path

import numpy as np

MODULE3 = Path(__file__).resolve().parents[2] / "team_06_module3"
sys.path.insert(0, str(MODULE3))

from board_link import Board
from team_audio import clip_list, get_clip

TEAM = 6
FS = 16000
WIN = 480
HOP = 320
NFFT = 512
MELS = 40
PACKET_SIZE = 320

SKIP_PACKETS = (10, 11, 200)

OUT = Path(__file__).resolve().parents[1] / "results"
OUT.mkdir(parents=True, exist_ok=True)


def to_i16_payload(audio):
    audio = np.asarray(audio, dtype=np.float32)
    audio = np.clip(audio, -1.0, 1.0)
    return (audio * 32767).astype("<i2").tobytes()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True)
    parser.add_argument("--baud", type=int, default=921600)
    parser.add_argument("--speed", type=float, default=1.0)

    args = parser.parse_args()

    clips = clip_list(TEAM)

    audio_parts = []
    clip_boundaries = []
    cursor = 0

    print(f"Loading {len(clips)} clips...")

    for clip_id, label in clips:
        audio = get_clip(TEAM, clip_id, fs=FS)
        audio = np.asarray(audio, dtype=np.float32)

        start = cursor
        end = start + len(audio)

        audio_parts.append(audio)
        clip_boundaries.append({
            "clip_id": int(clip_id),
            "label": str(label),
            "start_sample": start,
            "end_sample": end,
            "samples": len(audio),
        })

        cursor = end

    combined_audio = np.concatenate(audio_parts)
    payload = to_i16_payload(combined_audio)

    total_samples = len(combined_audio)
    expected_packets = (total_samples + PACKET_SIZE - 1) // PACKET_SIZE

    print("\nCONTINUOUS PACKET LOSS EXPERIMENT")
    print("--------------------------------")
    print(f"Clips: {len(clips)}")
    print(f"Total samples: {total_samples}")
    print(f"Expected packets: {expected_packets}")
    print(f"Skipped packet indices: {SKIP_PACKETS}")
    print(f"Packets expected to be sent: {expected_packets - len(SKIP_PACKETS)}")
    print(f"Serial port: {args.port}")

    board = Board(args.port, args.baud)

    try:
        if not board.ping():
            raise RuntimeError("ESP32 did not respond to PING")

        print("\nESP32 connection: OK")
        print("Streaming the complete dataset as ONE continuous stream...")

        result = board.stream(
            payload=payload,
            fs=FS,
            fmt="i16",
            win=WIN,
            hop=HOP,
            nfft=NFFT,
            mels=MELS,
            mfcc=0,
            feat=True,
            store="none",
            speed=args.speed,
            samples_per_packet=PACKET_SIZE,
            skip=SKIP_PACKETS,
        )

    finally:
        board.close()
        print("Serial connection closed.")

    features = result["features"]
    first_samples = np.asarray(result["first_sample"], dtype=np.int64)
    board_summary = result["board"] or {}

    # Assign every received feature frame to its source clip.
    frame_labels = []
    frame_clip_ids = []
    frame_status = []

    for first in first_samples:
        window_start = int(first)
        window_end = window_start + WIN

        matching_clip = None

        for clip in clip_boundaries:
            if (
                window_start >= clip["start_sample"]
                and window_end <= clip["end_sample"]
            ):
                matching_clip = clip
                break

        if matching_clip is not None:
            frame_labels.append(matching_clip["label"])
            frame_clip_ids.append(matching_clip["clip_id"])
            frame_status.append("single_clip")
        else:
            # The window overlaps a clip boundary.
            frame_labels.append("boundary_mixed")
            frame_clip_ids.append(-1)
            frame_status.append("boundary_mixed")

    # Identify the original sample intervals omitted by the test.
    missing_sample_intervals = []

    for packet_index in SKIP_PACKETS:
        start = packet_index * PACKET_SIZE
        end = min(start + PACKET_SIZE, total_samples)
        missing_sample_intervals.append([start, end])

    received_frames = len(features)
    expected_baseline_frames = (
        1 + (total_samples - WIN) // HOP
        if total_samples >= WIN else 0
    )

    report = {
        "experiment": "mission_4_continuous_packet_loss",
        "team": TEAM,
        "clips": len(clips),
        "sampling_rate": FS,
        "window": WIN,
        "hop": HOP,
        "samples_per_packet": PACKET_SIZE,
        "total_samples": total_samples,
        "expected_input_packets": expected_packets,
        "skipped_packets": list(SKIP_PACKETS),
        "packets_sent": result["packets_sent"],
        "samples_received": board_summary.get("samples"),
        "timeline_samples": board_summary.get("timeline_samples"),
        "sequence_gaps": board_summary.get("seq_gaps"),
        "input_crc_errors": board_summary.get("bad_crc"),
        "output_crc_errors": result["bad_crc_back"],
        "baseline_continuous_feature_frames": expected_baseline_frames,
        "received_feature_frames": received_frames,
        "feature_frames_not_received_vs_baseline":
            expected_baseline_frames - received_frames,
        "boundary_mixed_frames": frame_status.count("boundary_mixed"),
        "single_clip_labelled_frames": frame_status.count("single_clip"),
        "missing_sample_intervals": missing_sample_intervals,
        "board_summary": board_summary,
        "speed": args.speed,
    }

    # Save every received feature, including boundary-mixed frames.
    npz_path = OUT / "continuous_loss_dataset.npz"

    np.savez_compressed(
        npz_path,
        features=features,
        labels=np.asarray(frame_labels),
        clip_id=np.asarray(frame_clip_ids, dtype=np.int32),
        first_sample=first_samples,
        frame_status=np.asarray(frame_status),
    )

    # Save the clip-to-sample mapping.
    boundaries_path = OUT / "continuous_clip_boundaries.csv"

    with boundaries_path.open("w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=clip_boundaries[0].keys()
        )
        writer.writeheader()
        writer.writerows(clip_boundaries)

    # Save experiment summary.
    json_path = OUT / "continuous_loss_summary.json"
    json_path.write_text(json.dumps(report, indent=4))

    print("\n========== CONTINUOUS LOSS RESULTS ==========")
    print(json.dumps(report, indent=4))

    print("\nSaved files:")
    print(npz_path)
    print(boundaries_path)
    print(json_path)


if __name__ == "__main__":
    main()
