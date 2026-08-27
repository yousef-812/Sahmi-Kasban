#!/usr/bin/env bash
set -e
rm -rf /tmp/bt_output
mkdir -p /tmp/bt_output/candles
tar -xzf /tmp/candles.tar.gz -C /tmp/bt_output ./universe.json
cd /workspace/backend
nohup python /tmp/06_server_run.py 2022 2023 2024 2025 > /tmp/bt.log 2>&1 &
echo "PID=$!"
