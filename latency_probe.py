import csv
import socket
import time
from datetime import datetime

from detect import compute_baseline, is_anomalous

TARGETS = [
    ("google_dns_tcp", "8.8.8.8", 443),
    ("cloudflare_dns_tcp", "1.1.1.1", 443),
    ("github_https", "github.com", 443),
]

SAMPLES_PER_TARGET = 12
BASELINE_SAMPLES = 6
THRESHOLD_SIGMA = 2.0
SLEEP_SEC = 0.5
CONNECT_TIMEOUT_SEC = 2.0


def tcp_rtt_ms(host: str, port: int) -> float | None:
    """
    Measure "RTT" as TCP connect time to (host, port).

    """
    try:
        start = time.perf_counter()
        with socket.create_connection((host, port), timeout=CONNECT_TIMEOUT_SEC):
            end = time.perf_counter()
        return (end - start) * 1000.0
    except Exception:
        return None


def main():
    ts = datetime.now().isoformat(timespec="seconds").replace(":", "-")
    out_file = f"rtt_results_{ts}.csv"
    print(f"Writing results to: {out_file}\n")

    rows = []

    for name, host, port in TARGETS:
        print(f"== Target: {name} ({host}:{port}) ==")

        successes = []
        for i in range(1, SAMPLES_PER_TARGET + 1):
            rtt = tcp_rtt_ms(host, port)

            if rtt is None:
                print(f"[{i:02d}] timeout/fail")
            else:
                print(f"[{i:02d}] {rtt:.2f} ms")
                successes.append(rtt)

            rows.append({
                "timestamp": datetime.now().isoformat(timespec="seconds"),
                "target_name": name,
                "host": host,
                "port": port,
                "sample_index": i,
                "rtt_ms": "" if rtt is None else f"{rtt:.3f}",
            })

            time.sleep(SLEEP_SEC)

        if len(successes) >= BASELINE_SAMPLES + 2:
            baseline = successes[:BASELINE_SAMPLES]
            mean, std = compute_baseline(baseline)

            print(f"\nBaseline (first {BASELINE_SAMPLES} successes): mean={mean:.2f} ms, std={std:.2f} ms")
            for j, rtt in enumerate(successes[BASELINE_SAMPLES:], start=BASELINE_SAMPLES + 1):
                status = "ANOMALY" if is_anomalous(rtt, mean, std, threshold=THRESHOLD_SIGMA) else "ok"
                print(f"  success {j:02d}: {rtt:.2f} ms -> {status}")
        else:
            print("\nNot enough successful samples to compute baseline.")

        print()

    with open(out_file, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["timestamp", "target_name", "host", "port", "sample_index", "rtt_ms"]
        )
        writer.writeheader()
        writer.writerows(rows)

    print("Done.")


if __name__ == "__main__":
    main()


