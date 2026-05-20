#!/usr/bin/env python3
"""
Memory Freeze Dashboard

Web dashboard for monitoring the memory freeze tool.
"""

from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO, emit
import json
import os
import threading
import time
from shared_state import read_state

app = Flask(__name__)
app.config['SECRET_KEY'] = 'memfreeze-secret!'
socketio = SocketIO(app)

STATE_FILE = "memfreeze_state.json"

def background_thread():
    """Background thread to emit state updates via SocketIO."""
    while True:
        state = read_state()
        socketio.emit('state_update', state)
        time.sleep(2)  # Emit every 2 seconds

@app.route('/')
def index():
    """Render the main dashboard."""
    return render_template('dashboard.html')

@app.route('/api/state')
def api_state():
    """API endpoint to get current state."""
    return jsonify(read_state())

@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    print('Client connected')
    # Send current state immediately
    emit('state_update', read_state())

def start_background_thread():
    """Start the background thread for emitting updates."""
    thread = threading.Thread(target=background_thread)
    thread.daemon = True
    thread.start()

if __name__ == '__main__':
    # Start background thread
    start_background_thread()
    # Run the app
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)