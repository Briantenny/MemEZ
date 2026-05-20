#!/usr/bin/env python3
"""
Memory Freeze Tool - Main Entry Point

This script starts both the memory monitor and the web dashboard.
For production use, consider running them as separate services.
"""

import subprocess
import sys
import time
import threading
import os

def run_monitor():
    """Run the memory freeze monitor."""
    print("Starting memory freeze monitor...")
    subprocess.run([sys.executable, "memfreeze_monitor.py"])

def run_dashboard():
    """Run the web dashboard."""
    print("Starting web dashboard...")
    subprocess.run([sys.executable, "dashboard.py"])

def main():
    """Start both monitor and dashboard in separate threads."""
    print("=== Memory Freeze Tool ===")
    print("Starting monitoring and dashboard services...\n")
    
    # Start monitor in background thread
    monitor_thread = threading.Thread(target=run_monitor, daemon=True)
    monitor_thread.start()
    
    # Give monitor a moment to start
    time.sleep(2)
    
    # Start dashboard in background thread
    dashboard_thread = threading.Thread(target=run_dashboard, daemon=True)
    dashboard_thread.start()
    
    try:
        # Keep main thread alive
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nShutting down Memory Freeze Tool...")
        print("Note: Monitor and dashboard will stop when this process ends.")
        sys.exit(0)

if __name__ == "__main__":
    main()