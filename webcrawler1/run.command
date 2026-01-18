#!/bin/bash
cd "$(dirname "$0")"
uv run python -m ai_pulse_monitor.main --sync
echo ""
echo "按 Enter 關閉視窗..."
read
