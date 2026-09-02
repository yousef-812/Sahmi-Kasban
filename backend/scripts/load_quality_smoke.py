from __future__ import annotations

import asyncio
import math
import time

import httpx

from app.main import app

REQUEST_COUNT = 200
CONCURRENCY = 25
P95_BUDGET_MS = 1_000.0


async def run_request(client: httpx.AsyncClient, semaphore: asyncio.Semaphore) -> tuple[int, float, str]:
    async with semaphore:
        started = time.perf_counter()
        response = await client.get("/api/v1/health")
        duration_ms = (time.perf_counter() - started) * 1000
        return response.status_code, duration_ms, response.headers.get("x-request-id", "")


async def main() -> None:
    transport = httpx.ASGITransport(app=app)
    semaphore = asyncio.Semaphore(CONCURRENCY)
    async with httpx.AsyncClient(
        transport=transport,
        base_url="http://quality.test",
        timeout=10.0,
    ) as client:
        results = await asyncio.gather(*(run_request(client, semaphore) for _ in range(REQUEST_COUNT)))

    statuses = [status for status, _, _ in results]
    latencies = sorted(duration for _, duration, _ in results)
    request_ids = [request_id for _, _, request_id in results]
    p95_index = max(0, math.ceil(len(latencies) * 0.95) - 1)
    p95 = latencies[p95_index]

    if any(status != 200 for status in statuses):
        raise SystemExit(f"Load smoke returned non-200 statuses: {set(statuses)}")
    if any(not request_id for request_id in request_ids):
        raise SystemExit("Load smoke found a response without X-Request-ID")
    if len(set(request_ids)) != REQUEST_COUNT:
        raise SystemExit("Load smoke found duplicate generated request IDs")
    if p95 > P95_BUDGET_MS:
        raise SystemExit(f"Load smoke P95 {p95:.2f}ms exceeded budget {P95_BUDGET_MS:.2f}ms")

    print(
        "Load smoke passed: "
        f"requests={REQUEST_COUNT} concurrency={CONCURRENCY} "
        f"p95_ms={p95:.2f} max_ms={latencies[-1]:.2f}"
    )


if __name__ == "__main__":
    asyncio.run(main())
