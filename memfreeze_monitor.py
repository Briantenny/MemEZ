#!/usr/bin/env python3
"""
Memory Freeze Monitor

Monitors system memory usage and automatically freezes (SIGSTOP) processes
that are consuming excessive memory, resuming them (SIGCONT) when memory
pressure subsides.
"""

import json
import os
import signal
import time
import psutil
from shared_state import read_state, write_state, get_default_state

# Configuration
MEMORY_THRESHOLD_PERCENT = 85.0      # Freeze when system memory > this %
MEMORY_RESUME_THRESHOLD_PERCENT = 70.0  # Resume when system memory < this %
CHECK_INTERVAL = 5                   # Seconds between checks
FREEZE_THRESHOLD_COUNT = 3           # Consecutive high readings before freezing
RESUME_THRESHOLD_COUNT = 2           # Consecutive normal readings before resuming
MIN_PROCESS_MEMORY_MB = 50           # Only consider processes using at least this much memory
EXCLUDE_PIDS = {1, 2, 3, 4, 5}       # Never freeze these critical PIDs
EXCLUDE_NAMES = {'systemd', 'kernel', 'kthreadd', 'rcu_'}  # Never freeze processes with these names

def is_safe_to_freeze(proc):
    """Check if it's relatively safe to freeze a process."""
    try:
        # Don't freeze critical system processes
        if proc.pid in EXCLUDE_PIDS:
            return False
        
        # Don't freeze kernel threads or processes with scary names
        try:
            name = proc.name()
            for exclude in EXCLUDE_NAMES:
                if name.startswith(exclude):
                    return False
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            pass
        
        # Don't freeze processes we don't have permission to signal
        # (we'll test this when we actually try to signal)
        
        return True
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return False

def get_memory_usage():
    """Get system memory usage percentage."""
    mem = psutil.virtual_memory()
    return mem.percent

def get_top_processes(limit=10):
    """Get top memory-consuming processes."""
    processes = []
    for proc in psutil.process_iter(['pid', 'name', 'memory_info', 'username']):
        try:
            # Skip if not enough memory to worry about
            mem_mb = proc.info['memory_info'].rss / 1024 / 1024
            if mem_mb < MIN_PROCESS_MEMORY_MB:
                continue
                
            processes.append({
                'pid': proc.info['pid'],
                'name': proc.info['name'],
                'username': proc.info['username'],
                'memory_mb': round(mem_mb, 1),
                'memory_percent': round(proc.info['memory_info'].rss / psutil.virtual_memory().total * 100, 1)
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass
    
    # Sort by memory usage descending
    processes.sort(key=lambda x: x['memory_mb'], reverse=True)
    return processes[:limit]

def freeze_process(pid):
    """Freeze a process using SIGSTOP."""
    try:
        os.kill(pid, signal.SIGSTOP)
        return True
    except (ProcessLookupError, PermissionError):
        return False

def resume_process(pid):
    """Resume a frozen process using SIGCONT."""
    try:
        os.kill(pid, signal.SIGCONT)
        return True
    except (ProcessLookupError, PermissionError):
        return False

def main():
    """Main monitoring loop."""
    print("Starting Memory Freeze Monitor...")
    print(f"Will freeze processes when memory > {MEMORY_THRESHOLD_PERCENT}%")
    print(f"Will resume processes when memory < {MEMORY_RESUME_THRESHOLD_PERCENT}%")
    print(f"Check interval: {CHECK_INTERVAL} seconds")
    print("Press Ctrl+C to stop\n")
    
    # State tracking for hysteresis
    freeze_counters = {}  # pid -> consecutive high memory count
    resume_counters = {}  # pid -> consecutive normal memory count
    currently_frozen = set()  # pids we have frozen
    
    try:
        while True:
            # Get current system state
            memory_percent = get_memory_usage()
            top_processes = get_top_processes()
            
            # Update hysteresis counters
            high_memory = memory_percent > MEMORY_THRESHOLD_PERCENT
            low_memory = memory_percent < MEMORY_RESUME_THRESHOLD_PERCENT
            
            # Track which PIDs we saw in this check
            seen_pids = {proc['pid'] for proc in top_processes}
            
            # Update counters for seen processes
            for proc in top_processes:
                pid = proc['pid']
                if not is_safe_to_freeze(psutil.Process(pid)):
                    continue
                    
                if high_memory:
                    freeze_counters[pid] = freeze_counters.get(pid, 0) + 1
                    resume_counters[pid] = 0  # reset resume counter
                else:
                    resume_counters[pid] = resume_counters.get(pid, 0) + 1
                    freeze_counters[pid] = 0  # reset freeze counter
            
            # Decay counters for unseen processes (they might have exited)
            # We'll let them expire naturally or handle via process lookup errors
            
            # Freeze processes that have exceeded threshold
            if high_memory:
                for proc in top_processes:
                    pid = proc['pid']
                    if not is_safe_to_freeze(psutil.Process(pid)):
                        continue
                        
                    if freeze_counters.get(pid, 0) >= FREEZE_THRESHOLD_COUNT:
                        if pid not in currently_frozen:
                            if freeze_process(pid):
                                currently_frozen.add(pid)
                                print(f"FROZE: {proc['name']} (PID {pid}) - {proc['memory_mb']} MB")
                            else:
                                print(f"FAILED to freeze: {proc['name']} (PID {pid})")
            
            # Resume processes that have been normal long enough
            else:  # low memory or normal
                to_resume = []
                for pid in list(currently_frozen):  # copy because we'll modify set
                    if resume_counters.get(pid, 0) >= RESUME_THRESHOLD_COUNT:
                        to_resume.append(pid)
                
                for pid in to_resume:
                    try:
                        proc = psutil.Process(pid)
                        if resume_process(pid):
                            currently_frozen.remove(pid)
                            print(f"RESUMED: {proc.name()} (PID {pid})")
                        else:
                            print(f"FAILED to resume: {proc.name()} (PID {pid})")
                            # Keep in frozen set? Maybe try again next time
                    except psutil.NoSuchProcess:
                        # Process exited, remove from our tracking
                        currently_frozen.discard(pid)
            
            # Prepare state for dashboard
            state = get_default_state()
            state['memory_percent'] = round(memory_percent, 1)
            state['frozen_processes'] = list(currently_frozen)
            state['top_processes'] = top_processes
            state['system_info'] = {
                'cpu_percent': psutil.cpu_percent(interval=0.1),
                'boot_time': psutil.boot_time(),
                'timestamp': time.time()
            }
            write_state(state)
            
            # Sleep until next check
            time.sleep(CHECK_INTERVAL)
            
    except KeyboardInterrupt:
        print("\nStopping Memory Freeze Monitor...")
        # Optionally resume all frozen processes before exiting
        if currently_frozen:
            print(f"Resuming {len(currently_frozen)} frozen processes...")
            for pid in list(currently_frozen):
                try:
                    proc = psutil.Process(pid)
                    resume_process(pid)
                    print(f"Resumed: {proc.name()} (PID {pid})")
                except psutil.NoSuchProcess:
                    pass
        print("Goodbye!")

if __name__ == "__main__":
    main()