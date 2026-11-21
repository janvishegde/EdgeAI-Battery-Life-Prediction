
import matplotlib.pyplot as plt
from pathlib import Path

OUT = Path(__file__).parent
OUT.mkdir(parents=True, exist_ok=True)

# Graph 1: Remote Keep-Alive request latency breakdown (p50)
stages = ["Parse", "Normalise", "Inference", "Build", "Server total", "Network + framework"]
values = [0.059, 0.051, 0.254, 0.026, 0.412, 47.606]

plt.figure(figsize=(10, 5))
plt.barh(stages, values)
plt.xlabel("Latency (ms)")
plt.title("Remote Keep-Alive: Median Request Latency Breakdown")
plt.tight_layout()
plt.savefig(OUT / "01_latency_breakdown.png", dpi=300)
plt.close()

# Graph 2: Keep-Alive vs No-Keep-Alive
metrics = ["p50", "p95", "p99"]
keep_alive = [48.091, 64.542, 149.417]
no_keep_alive = [157.450, 229.042, 276.376]

x = range(len(metrics))
width = 0.35

plt.figure(figsize=(9, 5))
plt.bar([i - width / 2 for i in x], keep_alive, width, label="Keep-Alive")
plt.bar([i + width / 2 for i in x], no_keep_alive, width, label="No-Keep-Alive")
plt.xticks(list(x), metrics)
plt.ylabel("Round-trip latency (ms)")
plt.title("Impact of HTTP Keep-Alive")
plt.legend()
plt.tight_layout()
plt.savefig(OUT / "02_keepalive_comparison.png", dpi=300)
plt.close()

# Graph 3: Remote vs Local median latency
configurations = ["Remote Keep-Alive", "Remote No-Keep-Alive", "Codespace Local"]
latencies = [48.091, 157.450, 2.208]

plt.figure(figsize=(10, 5))
plt.bar(configurations, latencies)
plt.ylabel("Median round-trip latency (ms)")
plt.title("Remote vs Local API Performance")
plt.xticks(rotation=15, ha="right")
plt.tight_layout()
plt.savefig(OUT / "03_remote_vs_local.png", dpi=300)
plt.close()

# Graph 4: Individual requests vs batch processing
methods = ["400 Individual Requests", "1 Batch Request (400 rows)"]
total_times = [1304.48, 131.20]

plt.figure(figsize=(8, 5))
plt.bar(methods, total_times)
plt.ylabel("Total execution time (ms)")
plt.title("Individual Inference vs Batch Inference (400 Readings)")
plt.tight_layout()
plt.savefig(OUT / "04_batch_comparison.png", dpi=300)
plt.close()

print("Mission 3 graphs generated successfully:")
for file in sorted(OUT.glob("*.png")):
    print(file.name)
