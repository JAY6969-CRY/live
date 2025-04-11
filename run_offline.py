#!/usr/bin/env python
"""
Run NewsSense in offline mode without requiring API connections.
This is useful for demonstration purposes or when APIs are unavailable.
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

def run_streamlit_offline():
    """Run the Streamlit frontend in offline mode."""
    print("\nStarting Streamlit UI in OFFLINE MODE...")
    # Add the current directory to the Python path
    env = os.environ.copy()
    env["PYTHONPATH"] = os.getcwd() + os.pathsep + env.get("PYTHONPATH", "")
    
    # Set environment variables for Streamlit
    env["STREAMLIT_BROWSER_GATHER_USAGE_STATS"] = "false"
    
    # Create temp file with offline mode set to True
    with open("temp_offline_app.py", "w") as f:
        f.write("""
# Import the original app, but override OFFLINE_MODE
import os
import sys

# Add the current directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the original app content
with open('web/app.py', 'r') as original:
    original_content = original.read()

# Replace the offline mode flag
modified_content = original_content.replace('OFFLINE_MODE = False', 'OFFLINE_MODE = True')

# Execute the modified content
exec(modified_content)
""")
    
    # Start the process with offline mode
    process = subprocess.Popen(
        ["streamlit", "run", "temp_offline_app.py", "--server.port=8501"],
        env=env
    )
    
    # Wait a moment for Streamlit to start
    time.sleep(3)
    
    # Open the browser
    print("Opening web browser to http://localhost:8501")
    webbrowser.open("http://localhost:8501")
    
    print("\nStreamlit UI is running in OFFLINE MODE.")
    print("This means all data is simulated and no API connections are required.")
    print("Press Ctrl+C to stop.")
    
    # Keep the script running until Ctrl+C
    try:
        process.wait()
    except KeyboardInterrupt:
        print("\nStopping Streamlit...")
        process.terminate()
        process.wait()
        
        # Clean up the temp file
        if os.path.exists("temp_offline_app.py"):
            os.remove("temp_offline_app.py")
        
        print("Streamlit stopped.")

if __name__ == "__main__":
    run_streamlit_offline() 