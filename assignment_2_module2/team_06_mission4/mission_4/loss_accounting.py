"""
Mission 4 - Packet and feature-frame loss accounting.

Models the Team 6 stream:
    fs=16000, win=480, hop=320, samples_per_packet=320

Separates:
1. Input packets deliberately not sent.
2. Samples not processed by the board.
3. Feature windows affected by discontinuities in the input.
4. Feature responses missing from the laptop receiver.
"""

from dataclasses import dataclass, asdict
from typing import Iterable
import json
import math


@dataclass
class LossReport:
    total_samples: int
    expected_input_packets: int
    skipped_input_packets: list
    packets_sent: int
    samples_sent: int
    samples_not_processed: int
    firmware_samples_processed: int
    sample_accounting_matches: bool

    baseline_expected_features: int
    board_expected_features: int
    received_feature_frames: int
    missing_response_sequences: list
    missing_response_count: int
    feature_frames_not_generated_vs_baseline: int
    discontinuity_affected_frames: list
    discontinuity_affected_count: int

    input_crc_errors: int
    output_crc_errors: int
    firmware_sequence_gaps: int
    firmware_duplicates: int
    expected_firmware_valid_frames_including_end: int
    firmware_valid_frames_including_end: int


def expected_packets(total_samples, samples_per_packet):
    if total_samples < 0 or samples_per_packet <= 0:
        raise ValueError("Invalid sample or packet count")
    return math.ceil(total_samples / samples_per_packet)


def expected_features(total_samples, win=480, hop=320):
    if win <= 0 or hop <= 0:
        raise ValueError("Window and hop must be positive")
    if total_samples < win:
        return 0
    return 1 + (total_samples - win) // hop


def missing_sequences(received: Iterable[int], expected: int):
    received_set = set(int(x) for x in received)
    return sorted(set(range(expected)) - received_set)


def model_input_stream(
    total_samples,
    samples_per_packet=320,
    skipped_packets=(),
    win=480,
    hop=320,
):
    """
    Simulate the original sample index corresponding to every sample
    accepted by the board.

    A feature window is marked affected if it crosses a gap between
    original input sample positions.
    """
    packet_count = expected_packets(total_samples, samples_per_packet)
    skipped = sorted(set(int(x) for x in skipped_packets))

    invalid = [p for p in skipped if p < 0 or p >= packet_count]
    if invalid:
        raise ValueError(f"Invalid skipped packet indices: {invalid}")

    original_positions = []

    for packet in range(packet_count):
        if packet in skipped:
            continue

        start = packet * samples_per_packet
        end = min(start + samples_per_packet, total_samples)
        original_positions.extend(range(start, end))

    affected = []

    board_frames = expected_features(len(original_positions), win, hop)

    for frame_no in range(board_frames):
        start = frame_no * hop
        window_positions = original_positions[start:start + win]

        # A discontinuity occurs when consecutive accepted samples
        # did not come from consecutive original sample positions.
        has_gap = any(
            window_positions[i + 1] != window_positions[i] + 1
            for i in range(len(window_positions) - 1)
        )

        if has_gap:
            affected.append(frame_no)

    return original_positions, affected


def build_report(
    total_samples,
    samples_per_packet,
    skipped_packets,
    received_feature_sequences,
    firmware_samples_processed,
    input_crc_errors=0,
    output_crc_errors=0,
    firmware_sequence_gaps=0,
    firmware_duplicates=0,
    firmware_valid_frames_including_end=0,
    win=480,
    hop=320,
):
    packet_count = expected_packets(total_samples, samples_per_packet)
    skipped = sorted(set(int(x) for x in skipped_packets))

    original_positions, affected = model_input_stream(
        total_samples, samples_per_packet, skipped, win, hop
    )

    sent_packets = packet_count - len(skipped)
    samples_sent = len(original_positions)
    samples_not_processed = total_samples - samples_sent

    baseline_frames = expected_features(total_samples, win, hop)
    board_frames = expected_features(
        firmware_samples_processed, win, hop
    )

    received = [int(x) for x in received_feature_sequences]
    missing = missing_sequences(received, board_frames)

    expected_valid_frames = sent_packets + 1  # includes end marker

    return LossReport(
        total_samples=total_samples,
        expected_input_packets=packet_count,
        skipped_input_packets=skipped,
        packets_sent=sent_packets,
        samples_sent=samples_sent,
        samples_not_processed=samples_not_processed,
        firmware_samples_processed=firmware_samples_processed,
        sample_accounting_matches=(
            firmware_samples_processed == samples_sent
        ),

        baseline_expected_features=baseline_frames,
        board_expected_features=board_frames,
        received_feature_frames=len(set(received)),
        missing_response_sequences=missing,
        missing_response_count=len(missing),
        feature_frames_not_generated_vs_baseline=(
            baseline_frames - board_frames
        ),
        discontinuity_affected_frames=affected,
        discontinuity_affected_count=len(affected),

        input_crc_errors=input_crc_errors,
        output_crc_errors=output_crc_errors,
        firmware_sequence_gaps=firmware_sequence_gaps,
        firmware_duplicates=firmware_duplicates,
        expected_firmware_valid_frames_including_end=expected_valid_frames,
        firmware_valid_frames_including_end=firmware_valid_frames_including_end,
    )


def save_report(report, path):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(asdict(report), f, indent=4)


if __name__ == "__main__":
    # Simulated one-second input at 16 kHz.
    samples = 16000
    packet_size = 320
    skipped = [10, 11, 20]

    positions, affected = model_input_stream(
        samples, packet_size, skipped
    )

    processed_samples = len(positions)

    # Simulate all feature responses that the board should generate
    # from the samples it actually received.
    simulated_received = list(
        range(expected_features(processed_samples))
    )

    report = build_report(
        total_samples=samples,
        samples_per_packet=packet_size,
        skipped_packets=skipped,
        received_feature_sequences=simulated_received,
        firmware_samples_processed=processed_samples,
        firmware_sequence_gaps=len(skipped),
        firmware_valid_frames_including_end=48,
    )

    print(json.dumps(asdict(report), indent=4))
