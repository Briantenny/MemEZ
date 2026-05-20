# Memory Freeze Tool

A Linux utility that monitors memory usage and automatically freezes (SIGSTOP) processes consuming excessive memory, resuming them (SIGCONT) when memory pressure subsides. Includes a web dashboard for monitoring.

## Features

- Real-time memory usage monitoring
- Intelligent process freezing based on memory thresholds
- Automatic resumption when system stabilizes
- Web dashboard showing:
  - Current memory usage
  - Top memory-consuming processes
  - Currently frozen processes
  - Process status history
  - System load information
- Safe freezing/resuming using SIGSTOP/SIGCONT signals
- Configurable thresholds and monitoring intervals

## Architecture

```
memfreeze-tool/
├── memfreeze_monitor.py   # Background monitoring daemon
├── dashboard.py           # Flask web dashboard
├── shared_state.py        # Shared state between monitor and dashboard
├── requirements.txt       # Python dependencies
├── memfreeze.service      # Optional systemd service file
└── README.md
```

## Installation

1. Clone or copy this directory to your Linux system
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Configure thresholds in `memfreeze_monitor.py` if needed (default: freeze when system memory > 85%)
4. Run the monitor:
   ```bash
   python memfreeze_monitor.py
   ```
5. In another terminal, start the dashboard:
   ```bash
   python dashboard.py
   ```
6. Access dashboard at http://localhost:5000

## Configuration

Adjust these constants in `memfreeze_monitor.py`:

- `MEMORY_THRESHOLD_PERCENT` (default 85): System memory usage % above which freezing begins
- `MEMORY_RESUME_THRESHOLD_PERCENT` (default 70): System memory usage % below which processes resume
- `CHECK_INTERVAL` (default 5): Seconds between checks
- `FREEZE_THRESHOLD_COUNT` (default 3): Consecutive high-memory readings before freezing a process
- `RESUME_THRESHOLD_COUNT` (default 2): Consecutive normal readings before resuming a process

## Safety Notes

- The tool uses SIGSTOP/SIGCONT which pause/resume processes without terminating them
- Avoid freezing critical system processes (PID 1, kernel threads, etc.) - the monitor excludes PIDs < 100 by default
- Frozen processes continue to consume memory but not CPU
- Test on non-critical systems first

## Dashboard

Based on the ngx-admin inspiration, the dashboard provides:
- Real-time memory gauge
- Process tables with search/sort
- Visual indication of frozen processes
- Historical memory usage chart (using Chart.js)
- System information panel

## Requirements

- Python 3.6+
- psutil
- Flask
- Flask-SocketIO (for real-time updates)
- Optional: systemd for service management

## License

MIT