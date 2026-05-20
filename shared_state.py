import json
import os
import time

STATE_FILE = "memfreeze_state.json"

def read_state():
    """Read the shared state from file."""
    if not os.path.exists(STATE_FILE):
        return get_default_state()
    try:
        with open(STATE_FILE, 'r') as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return get_default_state()

def write_state(state):
    """Write the shared state to file."""
    state['timestamp'] = time.time()
    try:
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    except IOError as e:
        print(f"Error writing state file: {e}")

def get_default_state():
    """Return a default state structure."""
    return {
        "timestamp": 0,
        "memory_percent": 0.0,
        "frozen_processes": [],  # list of PIDs frozen by this tool
        "top_processes": [],     # list of dicts for top processes
        "system_info": {}
    }