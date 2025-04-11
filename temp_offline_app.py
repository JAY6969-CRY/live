
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
