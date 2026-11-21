import matplotlib.pyplot as plt

one_layer_params = [29, 57, 113, 225, 449]
one_layer_mae = [12.62, 18.55, 12.45, 12.51, 18.85]

two_layer_params = [49, 129, 385, 1281, 4609]
two_layer_mae = [10.53, 6.65, 6.14, 6.03, 5.98]

plt.figure(figsize=(9, 6))

plt.plot(one_layer_params, one_layer_mae, marker="o", label="One hidden layer")
plt.plot(two_layer_params, two_layer_mae, marker="s", label="Two hidden layers")

plt.xlabel("Number of Parameters")
plt.ylabel("Validation MAE (days)")
plt.title("Model Size vs Validation Error")

plt.legend()
plt.grid(True)
plt.tight_layout()
plt.xscale("log")

plt.savefig("model_comparison.png")
print("Graph saved successfully!")