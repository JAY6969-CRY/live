#!/usr/bin/env python
"""
Simple startup script for NewsSense direct integration.
This script launches the Streamlit UI with all components directly integrated.
"""
import os
import sys
import subprocess
import webbrowser
import time
import threading
from dotenv import load_dotenv

def main():
    """Main function to start the application."""
    # Load environment variables from .env file
    print("Loading environment variables from .env file...")
    load_dotenv()
    
    # Check for Gemini API key
    if "GEMINI_API_KEY" not in os.environ:
        print("WARNING: GEMINI_API_KEY environment variable is not set.")
        print("The QA system will use simulated responses without a Gemini API key.")
        print("You can set it with: export GEMINI_API_KEY=your_key_here")
        print("Or create a .env file with GEMINI_API_KEY=your_key_here")
    else:
        print("✓ Gemini API key detected! The QA system will use Gemini for enhanced responses.")
    
    # Start the Streamlit UI with direct integration
    print("\nStarting NewsSense with direct integration...")
    
    # Add the current directory to the Python path
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    
    # Start Streamlit with run_direct.py
    process = subprocess.Popen(
        ["streamlit", "run", "run_direct.py"],
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    print("Waiting for application to start...")
    time.sleep(3)
    
    # Monitor the process output
    def monitor_output():
        while True:
            output = process.stdout.readline()
            if output:
                print(output.strip())
            if process.poll() is not None:
                break
            error = process.stderr.readline()
            if error:
                print(f"[ERROR] {error.strip()}")
    
    # Start monitoring in a separate thread
    threading.Thread(target=monitor_output, daemon=True).start()
    
    # Open browser automatically
    print("Opening web browser...")
    webbrowser.open("http://localhost:8501")
    
    print("\nNewsSense is running at http://localhost:8501")
    print("Press Ctrl+C to stop the application")
    
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nShutting down...")
        process.terminate()
        process.wait()
        print("Application stopped.")

if __name__ == "__main__":
    main() 