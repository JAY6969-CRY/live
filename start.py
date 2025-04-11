#!/usr/bin/env python
"""
Startup script for NewsSense components.
This script starts the FastAPI server, Flask API server, and Streamlit UI.
"""
import os
import sys
import time
import subprocess
import webbrowser
import signal
import threading
import requests
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
print("Loading environment variables from .env file...")
load_dotenv()

# Check if Gemini API key is set
if "GEMINI_API_KEY" not in os.environ:
    print("WARNING: GEMINI_API_KEY environment variable is not set.")
    print("The QA system will use simulated responses without a Gemini API key.")
    print("You can set it with: export GEMINI_API_KEY=your_key_here")
    print("Or create a .env file with GEMINI_API_KEY=your_key_here")
    response = input("Continue anyway? (y/n): ")
    if response.lower() != "y":
        sys.exit(0)
else:
    print("✓ Gemini API key detected! The QA system will use Gemini for enhanced responses.")

processes = []

def start_fastapi():
    """Start the FastAPI server."""
    print("Starting FastAPI server...")
    # Add the current directory to the Python path
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    
    process = subprocess.Popen(
        ["uvicorn", "src.api.app:app", "--reload", "--host", "0.0.0.0", "--port", "8000"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    processes.append(process)
    print(f"FastAPI server is running at http://localhost:8000")
    return process

def start_flask():
    """Start the Flask API server."""
    print("Starting Flask API server...")
    # Add the current directory to the Python path
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    
    process = subprocess.Popen(
        ["python", "src/api/flask_app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        env=env
    )
    processes.append(process)
    print(f"Flask API server is running at http://localhost:5000")
    return process

def start_streamlit():
    """Start the Streamlit UI."""
    print("Starting Streamlit UI...")
    process = subprocess.Popen(
        ["streamlit", "run", "web/app.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    processes.append(process)
    print(f"Streamlit UI is running at http://localhost:8501")
    return process

def monitor_process(process, name):
    """Monitor a process and print its output."""
    while True:
        output = process.stdout.readline()
        if output:
            print(f"[{name}] {output.strip()}")
        if process.poll() is not None:
            break
        error = process.stderr.readline()
        if error:
            print(f"[{name} ERROR] {error.strip()}")

def open_browser():
    """Open the browser to the Streamlit UI."""
    time.sleep(3)  # Wait for Streamlit to start
    print("Opening browser...")
    webbrowser.open("http://localhost:8501")

def handle_exit(signum, frame):
    """Handle the exit signal."""
    print("\nShutting down all processes...")
    for process in processes:
        process.terminate()
    
    # Wait for processes to terminate
    for process in processes:
        process.wait()
    
    print("All processes terminated.")
    sys.exit(0)

def main():
    """Main function."""
    # Register signal handler for Ctrl+C
    signal.signal(signal.SIGINT, handle_exit)
    signal.signal(signal.SIGTERM, handle_exit)
    
    # Start all components in the correct order
    print("\n1. Starting FastAPI server (main backend)...")
    fastapi_process = start_fastapi()
    print("Waiting for FastAPI to initialize...")
    time.sleep(5)  # Increased wait time
    
    print("\n2. Starting Flask API server (stock analysis)...")
    flask_process = start_flask()
    print("Waiting for Flask API to initialize...")
    time.sleep(5)  # Increased wait time
    
    print("\n3. Starting Streamlit UI (frontend)...")
    streamlit_process = start_streamlit()
    print("Waiting for Streamlit to initialize...")
    time.sleep(5)  # Increased wait time
    
    # Check if APIs are responsive
    print("\nVerifying API endpoints...")
    fastapi_ok = False
    flask_ok = False
    
    # Try multiple times with longer timeouts
    for attempt in range(3):
        try:
            response = requests.get("http://localhost:8000", timeout=5)  # Increased timeout
            if response.status_code == 200:
                print("✓ FastAPI is responsive!")
                fastapi_ok = True
                break
            else:
                print(f"Attempt {attempt+1}: FastAPI returned status code: {response.status_code}")
        except Exception as e:
            print(f"Attempt {attempt+1}: FastAPI is not responsive: {str(e)}")
            time.sleep(2)
    
    for attempt in range(3):
        try:
            response = requests.get("http://localhost:5000", timeout=5)  # Increased timeout
            if response.status_code == 200:
                print("✓ Flask API is responsive!")
                flask_ok = True
                break
            else:
                print(f"Attempt {attempt+1}: Flask API returned status code: {response.status_code}")
        except Exception as e:
            print(f"Attempt {attempt+1}: Flask API is not responsive: {str(e)}")
            time.sleep(2)
    
    if not (fastapi_ok and flask_ok):
        print("\n⚠️ Warning: Some API endpoints may not be functioning correctly.")
        print("The application will continue to run, but some features may not work as expected.")
        print("You may need to restart the application if you encounter issues.")
        
        # Ask if the user wants to continue anyway
        response = input("Continue anyway? (y/n): ")
        if response.lower() != "y":
            handle_exit(None, None)
            return
    else:
        print("\n✓ All APIs are up and running!")
    
    # Open browser
    print("\nOpening web browser to Streamlit UI...")
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Monitor processes in separate threads
    threading.Thread(target=monitor_process, args=(fastapi_process, "FastAPI"), daemon=True).start()
    threading.Thread(target=monitor_process, args=(flask_process, "Flask"), daemon=True).start()
    threading.Thread(target=monitor_process, args=(streamlit_process, "Streamlit"), daemon=True).start()
    
    print("\nAll services are running. Press Ctrl+C to stop all services.")
    
    # Keep the main thread alive
    try:
        while all(process.poll() is None for process in processes):
            time.sleep(1)
    except KeyboardInterrupt:
        handle_exit(None, None)
    
    # If we get here, one of the processes has terminated
    print("One of the processes has terminated unexpectedly.")
    handle_exit(None, None)

if __name__ == "__main__":
    main() 