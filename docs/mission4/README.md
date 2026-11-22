---

## 6. Width-Scaling Experiment

To evaluate deployment feasibility for different model sizes, the network architecture was generalized to:

**5 → w → w → 1**

The parameter count is:

P = w² + 8w + 1

Memory requirements:

- Float32 = P × 4 bytes
- INT8 = P × 1 byte

MACs per prediction:

MACs = w² + 6w

The following table compares different hidden-layer widths:

| Width | Parameters | FP32 (Bytes) | INT8 (Bytes) | MACs |
|---:|---:|---:|---:|---:|
| 32 | 1,281 | 5,124 | 1,281 | 1,216 |
| 128 | 17,409 | 69,636 | 17,409 | 17,152 |
| 256 | 67,585 | 270,340 | 67,585 | 67,072 |
| 512 | 266,241 | 1,064,964 | 266,241 | 265,216 |
| 2048 | 4,210,689 | 16,842,756 | 4,210,689 | 4,206,592 |

These calculations were automated using `scripts/mission4_width_analysis.py`.

---

## 7. SRAM and PSRAM Fit Analysis

The model sizes were compared against the available memory budgets.

- SRAM budget: 300 KB = 307,200 bytes
- PSRAM: 8 MB = 8,388,608 bytes

| Width | SRAM FP32 | SRAM INT8 | PSRAM FP32 | PSRAM INT8 |
|---:|:---:|:---:|:---:|:---:|
| 32 | Yes | Yes | Yes | Yes |
| 128 | Yes | Yes | Yes | Yes |
| 256 | Yes | Yes | Yes | Yes |
| 512 | No | Yes | Yes | Yes |
| 2048 | No | No | No | Yes |

The comparison considers only model weights and biases. Additional memory is required for activations, runtime buffers, stack, and application components.

---

## 8. Maximum Hidden Width Within SRAM

For the architecture 5 → w → w → 1:

P = w² + 8w + 1

Using the 300 KB SRAM budget, the maximum hidden width was calculated for each precision.

| Precision | Maximum Width | Weight Memory |
|---|---:|---:|
| Float32 | 273 | 306,856 bytes |
| INT8 | 550 | 306,901 bytes |

At the next width, the model exceeds the assumed SRAM budget.

These are theoretical weight-storage limits. A practical deployment should use a smaller width to leave sufficient memory for activations and runtime overhead.

---

## 9. Prediction-Time Estimate

The current model requires 1,216 MACs per prediction.

Assuming an effective processing throughput of 10 MMAC/s:

Prediction time = MACs / Throughput

Prediction time = 1,216 / 10,000,000

Prediction time = 0.0001216 seconds

**Estimated arithmetic time = 0.122 ms per prediction.**

This is a theoretical estimate based on assumed throughput, not an actual measurement on the ESP32-S3.

Real inference time may be higher due to memory access, preprocessing, runtime overhead, scheduling, and implementation-specific optimizations.

---

## 10. Edge vs. Server Deployment

### On-Device Inference

Advantages:

- Low latency without network communication.
- Improved privacy as sensor data can remain locally processed.
- No per-prediction server cost.
- Predictions continue even when Wi-Fi is unavailable.
- Reduced dependency on cloud connectivity.

Limitations:

- Limited memory and computational resources.
- Model size and complexity must be carefully controlled.
- Model updates and monitoring are more challenging.

### Server-Based Inference

Advantages:

- Greater computational and memory resources.
- Centralized model deployment and updates.
- Easier monitoring, analytics, logging, and retraining.

Limitations:

- Network-dependent latency.
- Sensor data transmission may raise privacy concerns.
- Hosting and communication costs.
- Predictions may be unavailable during connectivity failure.

### Recommended Approach: Hybrid Architecture

The battery-life prediction model should run locally on the ESP32-S3 for fast predictions and offline operation.

The server can be used for:

- Historical data storage
- Visualization and dashboards
- Monitoring
- Analytics
- Model retraining
- Model updates

During Wi-Fi failure, the device should continue collecting readings and making predictions locally. Stored data can be synchronized when connectivity is restored.

---

## 11. Limitations and Assumptions

- The 300 KB SRAM budget is an assumed allocation for the model and application.
- Memory calculations include weights and biases only.
- INT8 calculations assume one byte per parameter and exclude quantization metadata and runtime overhead.
- Activation-memory estimates do not represent complete peak RAM usage.
- The prediction-time estimate is based on assumed throughput and has not been measured on the ESP32-S3.
- Actual deployment requires testing the model on hardware with a compatible embedded inference runtime.
- Accuracy, latency, memory usage, and power consumption must be validated on the target device.

---

## 12. Conclusion

The current 5 → 32 → 32 → 1 neural network is small enough to fit comfortably within the assumed ESP32-S3 SRAM budget in both Float32 and INT8 weight representations.

The width-scaling experiment demonstrates that model memory increases rapidly with hidden-layer width. INT8 quantization significantly reduces storage requirements and allows larger models to fit within the SRAM budget.

For this battery-life prediction task, on-device inference is feasible and offers low latency, privacy, reduced server dependency, and offline operation. A hybrid edge-cloud architecture provides the best balance by performing predictions locally while using the server for storage, monitoring, analytics, and model management.