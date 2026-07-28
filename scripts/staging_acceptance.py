#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import statistics
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class Sample:
    status: int
    elapsed_ms: float
    error: str | None = None


def request(url: str, *, timeout: float) -> Sample:
    started = time.perf_counter()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            response.read(64)
            status = response.status
        return Sample(status=status, elapsed_ms=(time.perf_counter() - started) * 1000)
    except urllib.error.HTTPError as exc:
        return Sample(
            status=exc.code,
            elapsed_ms=(time.perf_counter() - started) * 1000,
            error=str(exc),
        )
    except Exception as exc:  # noqa: BLE001 - operational smoke reports all failures.
        return Sample(
            status=0,
            elapsed_ms=(time.perf_counter() - started) * 1000,
            error=f"{type(exc).__name__}: {exc}",
        )


def percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if not ordered:
        return 0.0
    index = max(0, min(len(ordered) - 1, round((len(ordered) - 1) * fraction)))
    return ordered[index]


def main() -> int:
    parser = argparse.ArgumentParser(description="External Sahmi Kasban staging smoke")
    parser.add_argument(
        "--base-url",
        default="https://sahmi-kasban.fly.dev",
        help="Fly application root URL",
    )
    parser.add_argument("--requests", type=int, default=200)
    parser.add_argument("--concurrency", type=int, default=25)
    parser.add_argument("--timeout", type=float, default=15.0)
    parser.add_argument("--max-p95-ms", type=float, default=1000.0)
    args = parser.parse_args()

    base_url = args.base_url.rstrip("/")
    required_paths = (
        "/api/v1/health",
        "/api/v1/health/database",
        "/legal",
        "/privacy",
        "/terms",
        "/financial-disclaimer",
        "/data-safety",
        "/financial-features",
        "/delete-account",
    )
    failures: list[str] = []
    for path in required_paths:
        sample = request(f"{base_url}{path}", timeout=args.timeout)
        print(f"SMOKE {path}: status={sample.status} latency_ms={sample.elapsed_ms:.1f}")
        if sample.status != 200:
            failures.append(f"{path} returned {sample.status}: {sample.error or 'unexpected status'}")

    load_url = f"{base_url}/api/v1/health"
    samples: list[Sample] = []
    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as executor:
        futures = [
            executor.submit(request, load_url, timeout=args.timeout)
            for _ in range(max(1, args.requests))
        ]
        for future in as_completed(futures):
            samples.append(future.result())

    latencies = [sample.elapsed_ms for sample in samples]
    errors = [sample for sample in samples if sample.status != 200]
    summary = {
        "base_url": base_url,
        "requests": len(samples),
        "concurrency": args.concurrency,
        "successes": len(samples) - len(errors),
        "errors": len(errors),
        "average_ms": round(statistics.fmean(latencies), 2) if latencies else 0.0,
        "p50_ms": round(percentile(latencies, 0.50), 2),
        "p95_ms": round(percentile(latencies, 0.95), 2),
        "max_ms": round(max(latencies), 2) if latencies else 0.0,
    }
    print(json.dumps(summary, ensure_ascii=False, indent=2))

    if errors:
        failures.append(f"load smoke returned {len(errors)} failed requests")
    if summary["p95_ms"] > args.max_p95_ms:
        failures.append(
            f"load smoke p95 {summary['p95_ms']}ms exceeded {args.max_p95_ms}ms"
        )
    if failures:
        print("ACCEPTANCE FAILED", file=sys.stderr)
        for failure in failures:
            print(f"- {failure}", file=sys.stderr)
        return 1
    print("ACCEPTANCE PASSED")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
