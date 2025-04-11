 #!/usr/bin/env python
"""
Script to run just the Streamlit frontend of NewsSense.
This provides a fallback option when the APIs are not working properly.
"""
import os
import sys
import subprocess
import webbrowser
import time
from dotenv import load_dotenv

# Load environment variables from .env file if it exists
print("Loading environment variables from .env file...")
load_dotenv()

# Make sure the Gemini API key is available for mock responses
if "GEMINI_API_KEY" in os.environ:
    print(f"Found Gemini API key: {os.environ['GEMINI_API_KEY'][:5]}...{os.environ['GEMINI_API_KEY'][-4:]}")
else:
    print("Note: No Gemini API key found. Some features will use simulated responses.")

def run_streamlit():
    """Run the Streamlit frontend only."""
    print("\nStarting Streamlit UI...")
    # Add the current directory to the Python path
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    env["STREAMLIT_SERVER_HEADLESS"] = "false"  # Ensure not headless
    
    # Enable development mode for better error messages
    env["STREAMLIT_ENV"] = "development"
    
    # Create proxy configuration to allow offline mode
    env["STREAMLIT_SERVER_ENABLE_STATIC_SERVING"] = "true"
    
    # Start the process
    process = subprocess.Popen(
        ["streamlit", "run", "web/app.py", "--server.port=8501", "--server.enableCORS=true"],
        env=env
    )
    
    # Wait a moment for Streamlit to start
    time.sleep(3)
    
    # Open the browser
    print("Opening web browser to http://localhost:8501")
    webbrowser.open("http://localhost:8501")
    
    print("\nStreamlit UI is running. Press Ctrl+C to stop.")
    print("NOTE: Backend APIs are not running, so most features will show error messages.")
    
    # Keep the script running until Ctrl+C
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nStopping Streamlit...")
        process.terminate()
        process.wait()
        print("Streamlit stopped.")

if __name__ == "__main__":
    run_streamlit()