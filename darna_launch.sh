#!/bin/bash
#!/bin/bash
cd Health_server  # Change to the directory containing the 'server' folder
source darnavenv/bin/activate  # Activate the virtual environment
nohup python3 darna.py &

