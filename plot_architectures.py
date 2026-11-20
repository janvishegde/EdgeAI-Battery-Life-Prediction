import matplotlib.pyplot as plt
import numpy as np
# Single hidden layer experiments
single_layer = [
    (4, 29, 12.62),
    (8, 57, 18.55),
    (16, 113, 12.45),
    (32, 225, 12.51),
    (64, 449, 18.85),
]

# Two hidden layer experiments
two_layer = [
    ((4, 4), 49, 10.53),
    ((8, 8), 129, 6.65),
    ((16, 16), 385, 6.14),
    ((32, 32), 1281, 6.03),
    ((64, 64), 4609, 5.98),
]

# Extract parameter counts and validation errors
single_params = [item[1] for item in single_layer]
single_mae = [item[2] for item in single_layer]

two_params = [item[1] for item in two_layer]
two_mae = [item[2] for item in two_layer]
plt.figure(figsize=(10, 6))

plt.plot(single_params, single_mae, marker="o", label="1 Hidden Layer")
plt.plot(two_params, two_mae, marker="s", label="2 Hidden Layers")
plt.xscale("log")
plt.xlabel("Number of Parameters")
plt.ylabel("Validation MAE (days)")
plt.title("Model Size vs Validation Error")

plt.legend()
plt.grid(True)

plt.savefig("plots/mission2/architecture_comparison.png", dpi=300, bbox_inches="tight")
print("Graph saved successfully!")
for width, params, mae in single_layer:
    plt.annotate(str(width), (params, mae), xytext=(5, 5),
                 textcoords="offset points")

for widths, params, mae in two_layer:
    plt.annotate(str(widths[0]), (params, mae), xytext=(5, 5),
                 textcoords="offset points")