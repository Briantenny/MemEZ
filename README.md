<div align="center" markdown="1">

<img width="150" height="150" alt="ico" src="https://github.com/user-attachments/assets/df0d9742-2312-4da7-9876-a2bdd04b2ca2" />


# MemEZ Memory freeze tool
</div>
A Linux utility that monitors memory usage and automatically freezes (SIGSTOP) processes consuming excessive memory, resuming them (SIGCONT) when memory pressure subsides. Includes a web dashboard for monitoring.

<img width="1366" height="768" alt="Screenshot_2026-05-21_01_23_34" src="https://github.com/user-attachments/assets/8200aa34-ca25-4c3a-98ec-e1525f37aa25" />


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
3. Quick start:
   ```bash
   sudo python run.py
   ```
4. Access dashboard at http://localhost:5000
 
5. Configure thresholds in `memfreeze_monitor.py` if needed (default: freeze when system memory > 85%)


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

## Who is this tool for?

This tool helps prevent system crashes during memory- and CPU-intensive tasks.
- System administrators and DevOps engineers managing server stability and performance.  
- Software developers running heavy builds, compiles, or local container workloads.  
- Data scientists and ML engineers executing large model training or data-processing jobs.  
- QA engineers running extensive test suites or performance tests.  
- Power users running multiple resource-heavy applications concurrently.  
- IT support staff who need to troubleshoot and mitigate user-reported slowdowns or crashes.

## License

MIT
