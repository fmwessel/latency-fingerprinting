import csv
import glob
import os
from collections import defaultdict

import matplotlib.pyplot as plt

from detect import compute_baseline, is_anomalous

BASELINE_SAMPLES = 6
THRESHOLD_SIGMA = 2.0


def find_latest_csv():
    files = sorted(glob.glob("rtt_results_*.csv"))
    if not files:
        raise FileNotFoundError("No rtt_results_*.csv found. Run latency_probe.py first.")
    return files[-1]


def load_grouped(csv_path):
    grouped = defaultdict(list)
    with open(csv_path, "r", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            key = (row.get("target_name", "?"), row.get("host", "?"))
            s = (row.get("rtt_ms") or "").strip()
            grouped[key].append(float(s) if s else None)
    return grouped


def main():
    csv_path = find_latest_csv()
    grouped = load_grouped(csv_path)

    plt.figure()
    plt.title(f"RTT Over Time ({os.path.basename(csv_path)})")
    plt.xlabel("Sample Index")
    plt.ylabel("RTT (ms)")

    for (name, host), rtts in grouped.items():
        xs, ys = [], []
        for i, rtt in enumerate(rtts, start=1):
            if rtt is None:
                continue
            xs.append(i)
            ys.append(rtt)

        if not ys:
            continue

        # Baseline from first BASELINE_SAMPLES valid RTTs
        if len(ys) >= BASELINE_SAMPLES + 2:
            baseline = ys[:BASELINE_SAMPLES]
            mean, std = compute_baseline(baseline)

            normal_x, normal_y = [], []
            anomaly_x, anomaly_y = [], []

            for x, y in zip(xs, ys):
                if x <= BASELINE_SAMPLES:
                    normal_x.append(x); normal_y.append(y)
                elif is_anomalous(y, mean, std, threshold=THRESHOLD_SIGMA):
                    anomaly_x.append(x); anomaly_y.append(y)
                else:
                    normal_x.append(x); normal_y.append(y)

            plt.plot(xs, ys, label=f"{name} ({host})")
            plt.scatter(normal_x, normal_y, marker="o")
            plt.scatter(anomaly_x, anomaly_y, marker="x")
        else:
            plt.plot(xs, ys, marker="o", label=f"{name} ({host})")

    plt.legend()
    plt.tight_layout()
    plt.savefig("results.png", dpi=200)
    print("Saved results.png")


if __name__ == "__main__":
    main()

