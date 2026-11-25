import argparse
import csv
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, "team_06_module3")

from board_link import Board
from team_audio import clip_list, get_clip

TEAM = 6
FS = 16000
WIN = 480
HOP = 320
NFFT = 512
MELS = 40
SAMPLES_PER_PACKET = 320

OUT = Path("team_06_mission4/results")
OUT.mkdir(parents=True, exist_ok=True)


def to_i16_payload(audio):
    audio = np.asarray(audio, dtype=np.float32)
    audio = np.clip(audio, -1.0, 1.0)
    return (audio * 32767).astype("<i2").tobytes()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", required=True)
    parser.add_argument("--speed", type=float, default=1.0)
    args = parser.parse_args()

    clips = clip_list(TEAM)
    records = []
    all_features = []
    all_labels = []
    all_clip_ids = []
    all_first_samples = []

    board = Board(args.port)

    try:
        print("Board ping:", board.ping())
        print("Board info:", board.info())
        print(f"\nStarting {len(clips)} clips at speed={args.speed}\n")

        for index, (clip_id, label) in enumerate(clips, start=1):
            audio = get_clip(TEAM, clip_id, fs=FS)
            payload = to_i16_payload(audio)

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
                samples_per_packet=SAMPLES_PER_PACKET,
            )

            summary = result["board"] or {}
            features = result["features"]
            first_samples = result["first_sample"]

            expected_packets = (len(audio) + SAMPLES_PER_PACKET - 1) // SAMPLES_PER_PACKET
            expected_frames = (
                1 + (len(audio) - WIN) // HOP
                if len(audio) >= WIN else 0
            )

            record = {
                "clip_id": clip_id,
                "label": label,
                "samples_expected": len(audio),
                "packets_expected": expected_packets,
                "packets_sent": result["packets_sent"],
                "frames_ok": int(summary.get("frames_ok", -1)),
                "seq_gaps": int(summary.get("seq_gaps", -1)),
                "bad_crc": int(summary.get("bad_crc", -1)),
                "bad_len": int(summary.get("bad_len", -1)),
                "samples_received": int(summary.get("samples", -1)),
                "expected_features": expected_frames,
                "received_features": len(features),
                "lost_features": result["lost_features"],
                "output_crc_errors": result["bad_crc_back"],
                "first_sample_start": (
                    int(first_samples[0]) if len(first_samples) else None
                ),
                "first_sample_end": (
                    int(first_samples[-1]) if len(first_samples) else None
                ),
                "send_seconds": result["send_seconds"],
                "audio_seconds": result["audio_seconds"],
                "max_compute_us": int(summary.get("max_us", -1)),
                "avg_compute_us": int(summary.get("avg_us", -1)),
            }

            records.append(record)

            if len(features):
                all_features.append(features)
                all_labels.extend([label] * len(features))
                all_clip_ids.extend([clip_id] * len(features))
                all_first_samples.extend(first_samples.tolist())

            status = (
                "PASS"
                if (
                    record["packets_sent"] == 50
                    and record["frames_ok"] == 51
                    and record["seq_gaps"] == 0
                    and record["bad_crc"] == 0
                    and record["samples_received"] == 16000
                    and record["received_features"] == 49
                    and record["output_crc_errors"] == 0
                )
                else "CHECK"
            )

            print(
                f"[{index:03d}/144] clip={clip_id:03d} "
                f"label={label:9s} packets={record['packets_sent']} "
                f"samples={record['samples_received']} "
                f"features={record['received_features']} "
                f"gaps={record['seq_gaps']} "
                f"CRC={record['bad_crc']} -> {status}"
            )

    finally:
        board.close()

    # Save per-clip accounting.
    csv_path = OUT / "all_clips_accounting.csv"
    with csv_path.open("w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=records[0].keys())
        writer.writeheader()
        writer.writerows(records)

    # Save collected features with their labels and source coordinates.
    feature_matrix = (
        np.concatenate(all_features, axis=0)
        if all_features else np.zeros((0, MELS), dtype=np.float32)
    )

    npz_path = OUT / "all_clips_raw_features.npz"
    np.savez_compressed(
        npz_path,
        features=feature_matrix,
        labels=np.asarray(all_labels),
        clip_id=np.asarray(all_clip_ids, dtype=np.int32),
        first_sample=np.asarray(all_first_samples, dtype=np.int64),
    )

    total = {
        "clips_attempted": len(records),
        "clips_passed": sum(
            r["packets_sent"] == 50
            and r["frames_ok"] == 51
            and r["seq_gaps"] == 0
            and r["bad_crc"] == 0
            and r["samples_received"] == 16000
            and r["received_features"] == 49
            and r["output_crc_errors"] == 0
            for r in records
        ),
        "packets_sent": sum(r["packets_sent"] for r in records),
        "samples_received": sum(r["samples_received"] for r in records),
        "feature_frames_received": len(feature_matrix),
        "sequence_gaps": sum(max(0, r["seq_gaps"]) for r in records),
        "input_crc_errors": sum(max(0, r["bad_crc"]) for r in records),
        "output_crc_errors": sum(r["output_crc_errors"] for r in records),
        "feature_shape": list(feature_matrix.shape),
        "speed": args.speed,
    }

    json_path = OUT / "all_clips_summary.json"
    json_path.write_text(json.dumps(total, indent=2))

    print("\n========== FINAL ACCOUNTING ==========")
    print(json.dumps(total, indent=2))
    print("\nSaved:")
    print(csv_path)
    print(npz_path)
    print(json_path)


if __name__ == "__main__":
    main()
