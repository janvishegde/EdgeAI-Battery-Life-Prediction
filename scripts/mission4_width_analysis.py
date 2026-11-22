WIDTHS = [32, 128, 256, 512, 2048]

SRAM_BUDGET = 300 * 1024
PSRAM_BUDGET = 8 * 1024 * 1024

def calculate_model(width):
    layers = [(5, width), (width, width), (width, 1)]

    params = sum(i * o + o for i, o in layers)
    macs = sum(i * o for i, o in layers)

    f32_bytes = params * 4
    int8_bytes = params

    return {
        "width": width,
        "params": params,
        "f32_bytes": f32_bytes,
        "int8_bytes": int8_bytes,
        "macs": macs,
        "sram_f32": f32_bytes <= SRAM_BUDGET,
        "sram_int8": int8_bytes <= SRAM_BUDGET,
        "psram_f32": f32_bytes <= PSRAM_BUDGET,
        "psram_int8": int8_bytes <= PSRAM_BUDGET,
    }

print(f"{'Width':>6} {'Params':>12} {'F32 (B)':>12} {'INT8 (B)':>12} {'MACs':>12} {'SRAM F32':>10} {'SRAM INT8':>11} {'PSRAM F32':>11} {'PSRAM INT8':>12}")
print("-" * 110)

for width in WIDTHS:
    r = calculate_model(width)
    print(
        f"{r['width']:>6} {r['params']:>12,} "
        f"{r['f32_bytes']:>12,} {r['int8_bytes']:>12,} "
        f"{r['macs']:>12,} {str(r['sram_f32']):>10} "
        f"{str(r['sram_int8']):>11} {str(r['psram_f32']):>11} "
        f"{str(r['psram_int8']):>12}"
    )

print("\nMaximum hidden width fitting 300 KiB SRAM:")
for precision, bytes_per_param in [("float32", 4), ("int8", 1)]:
    max_width = 0
    for width in range(1, 10000):
        params = width**2 + 8*width + 1
        if params * bytes_per_param <= SRAM_BUDGET:
            max_width = width
        else:
            break
    print(f"{precision}: {max_width}")
