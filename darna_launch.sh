#!/bin/bash
#!/bin/bash
cd Health_server  # Change to the directory containing the 'server' folder
source darnav/bin/activate  # Activate the virtual environment
gunicorn -w 2 -b 0.0.0.0:3001 darna:app

