#!/usr/bin/env python3
#/* DARNA.HI
# * Copyright (c) 2023 Seapoe1809   <https://github.com/seapoe1809>
# * Copyright (c) 2023 pnmeka   <https://github.com/pnmeka>
# * 
# *
# *   This program is free software: you can redistribute it and/or modify
# *   it under the terms of the GNU General Public License as published by
# *   the Free Software Foundation, either version 3 of the License, or
# *   (at your option) any later version.
# *
# *   This program is distributed in the hope that it will be useful,
# *   but WITHOUT ANY WARRANTY; without even the implied warranty of
# *   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# *   GNU General Public License for more details.
# *
# *   You should have received a copy of the GNU General Public License
# *   along with this program. If not, see <http://www.gnu.org/licenses/>.
# */

import os
import subprocess
import webbrowser
import time
from pathlib import Path
import socket
import sys
import distro
import glob
import venv

##setup with git: sudo apt-get install git
##git clone"https://github.com/seapoe1809/Health_server"
##cd into the dir
##python3 setup_darna.py

##cmd to start process python3 setup_darna.py
print('*******************WELCOME TO DARNA Health Intent*************************')
print('********************self custody your health data*************************')
print('**************************************************************************')
print('*********|▓▓▓▗*****▓▚******▓▓▚***▓▚****▓*▓▚*********▓****▓*▓▓▓▓▓|*********')
print('*********|▓**▚▚\** ▓*▚*****▓**▚**▓*▚***▓*▓*▚********▓****▓***▓************')
print('*********|▓****▚|**▓**▚****▓**▞**▓**▍**▓*▓**▚*******▓****▓***▓************')
print('*********|▓****▞|**▓***▚***▓▓▚***▓**▐**▓*▓***▚******▓▓▓▓▓▓***▓************')
print('*********|▓**▚▞/***▓▓▓▓▓▚**▓**▚**▓***▚*▓*▓▓▓▓▓▚*****▓****▓***▓************')
print('*********|▓▓▞▘/****▓*****▚*▓***▚*▓****▚▓*▓*****▚*▓▓*▓****▓*▓▓▓▓▓|*********')
print('**************************************************************************')
print('        ☕ Step 1: Will try to install rsync to allow indexing Health_server files ☕,')
print('        ☕ Caffeine (to prevent the device from falling asleep while running Health_server.☕')
print('        ☕ Check for python version and install pip if needed ☕')
print('        ☕ Check for linux distro and install relevant modules ☕')

#get rsync to import zip files from Health_server
#get caffeine to help the computer stay awake and not fall asleep so it is available to nexcloud app
# Get the Python version
python_version = tuple(map(int, sys.version.split(" ")[0].split(".")))
min_version = (3, 8)

if python_version < min_version:
    print(f"Warning: You are using Python {'.'.join(map(str, python_version))}. The minimum required version is Python {'.'.join(map(str, min_version))}. Please update your Python installation and re-run setup.")
    sys.exit(1)

#prepare folderpaths 
HS_path = os.getcwd()
Health_files = os.path.join(HS_path, 'Health_files')
ocr_files = os.path.join(Health_files, 'ocr_files')
upload_dir = os.path.join(Health_files, 'upload')
summary_dir = os.path.join(Health_files, 'summary')


def run_common_commands():
    subprocess.run(['sudo', 'chmod', '750', 'Health_files/', 'Health_files2/'])
    # List all .sh files
    sh_files = glob.glob('*.sh')
    for sh_file in sh_files:
        subprocess.run(['sudo', 'chmod', '+x', sh_file])

def run_apt_commands():
    subprocess.run(['sudo', 'apt-get', 'update'])
    subprocess.run(['sudo', 'apt-get', 'install', '-y', 'rsync', 'caffeine', 'python3-pip', 'docker.io', 'tesseract-ocr', 'poppler-utils'])
    run_common_commands()

def run_dnf_commands():
    subprocess.run(['sudo', 'dnf', 'install', '-y', 'rsync', 'python3-pip', 'caffeine-ng', 'docker', 'tesseract', 'poppler-utils'])
    run_common_commands()

def run_yum_commands():
    subprocess.run(['sudo', 'yum', 'install', '-y', 'rsync', 'python3-pip', 'docker', 'tesseract', 'poppler-utils'])
    run_common_commands()

def run_pacman_commands():
    subprocess.run(['sudo', 'pacman', '-S', '--noconfirm', 'rsync', 'python-pip', 'caffeine-ng', 'docker', 'tesseract', 'poppler'])
    run_common_commands()

def run_zypper_commands():
    subprocess.run(['sudo', 'zypper', 'install', '-y', 'rsync', 'python3-pip', 'docker', 'tesseract', 'poppler-tools'])
    run_common_commands()

def run_platform_specific_commands():
    distro_name = distro.id()
    print(f"Detected distribution ID: {distro_name}")

    try:
        subprocess.run(['sudo', 'docker', 'version'], check=True)
        print('Good news, Docker already installed')
    except subprocess.CalledProcessError:
        print('Installing Docker...')
        
    if "ubuntu" in distro_name or "debian" in distro_name:
        run_apt_commands()
    elif "fedora" in distro_name:
        run_dnf_commands()
    elif "centos" in distro_name or "redhat" in distro_name:
        run_yum_commands()
    elif "arch" in distro_name:
        run_pacman_commands()
    elif "suse" in distro_name:
        run_zypper_commands()
    else:
        print("Unrecognized Linux distribution. Running Ubuntu commands by default.")
        run_apt_commands()

if __name__ == "__main__":
    run_platform_specific_commands()


#ip address generate
#get IP address
def get_ip_address():
    # Create a socket object
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # Connect to a remote server and get local IP address
        sock.connect(("8.8.8.8", 80))
        ip_address = sock.getsockname()[0]
    finally:
        # Close the socket
        sock.close()

    return ip_address

print('        ☕ Writing variables to variables.py ☕')
print('        ☕ Installing install_module from Git ☕')
print('        🢡 You could edit IP_address in variables.py if you ever change your device IP')



print('        ☕ Setting up virtual Env for Darna at darnavenv☕')
subprocess.run(['python3', '-m',  'venv', 'darnavenv'])
subprocess.run(["darnavenv/bin/pip", "install", "--force-reinstall", "-r", "requirements.txt"])
subprocess.run(["darnavenv/bin/python3", "setupapp.py"])

#set up darnabot
print('        ☕ Setting up virtual Env for Darnabot llmvenv. TensorRT required☕')
subprocess.run(['python3', '-m',  'venv', 'darnabot/llmvenv'])
subprocess.run(["darnabot/llmvenv/bin/pip", "install", "--force-reinstall", "-r", "darnabot/requirements.txt"])



ip_address = get_ip_address()
url =f'{ip_address}:3001'

content = f"HS_path = '{HS_path}'\nip_address= '{ip_address}'\nupload_dir ='{upload_dir}'\nHealth_files = '{Health_files}'\nocr_files = '{ocr_files}'\n"	

# Open the file in write mode and write the content
file_path =f'{HS_path}/variables/variables.py'
with open(file_path, 'w') as file:
    file.write(content) 

# Prepare the content for the .desktop file
content = f"""[Desktop Entry]
Name=DARNA.HI
Comment=Start darna.hi
Exec={HS_path}/darna_launch.sh
Icon={HS_path}/static/favicon.png
Terminal=true
Type=Application"""

# Define the path to the .desktop file
file_path = f'{HS_path}/darna.desktop'

# Open the file in write mode and write the content
with open(file_path, 'w') as file:
    file.write(content)
subprocess.run(['cp', 'darna.desktop', str(Path.home() / '.local' / 'share' / 'applications' / 'darna.desktop')])

# Prepare the content for the launch.sh file
content2 = f"""#!/bin/bash
cd {HS_path}
source darnavenv/bin/activate
#gunicorn -w 2 -b 0.0.0.0:3001 darna:app
nohup python3 darna.py &> darna.log &
nohup ./darnabot.sh &
"""

# Define the path to the .desktop file
file_path = f'{HS_path}/darna_launch.sh'

# Open the file in write mode and write the content
with open(file_path, 'w') as file:
    file.write(content2)
    
#prepare content and write to darnabot.sh file
#now using Ollama
content3 = f"""#!/bin/bash
cd {HS_path}/darnabot
source llmvenv/bin/activate
# Now using Ollama
# Set the environment variable HF_HOME
# export HF_HOME={HS_path}/darnabot/cache/hub
# export HUGGINGFACE_HUB_CACHE={HS_path}/darnabot/cache/huggingface/hub
# export TRANSFORMERS_CACHE={HS_path}/darnabot/cache/
nohup python3 darnabot.py &> darnabot.log &
"""

# Define the path to the .desktop file
file_path2 = f'{HS_path}/darnabot.sh'

# Open the file in write mode and write the content
with open(file_path2, 'w') as file:
    file.write(content3)


#lets all the above startup and subsequently opens browser
print('        🏃🏃 Waiting for final leg of installation to complete 🏃🏃')


#run caffeine as subprocess in background, start flask server and open browser with address.
caffeine_command= "caffeine &"
subprocess.run(caffeine_command, shell=True)

subprocess.run(['./darna_launch.sh'], shell=True)
print('        ☕ The server will be available at: ☕')
print(f"       ☕ On other devices, http://{ip_address}:3001 ☕ ")
print("        ☕ On same computer access at http://localhost:3001 ☕ ")
print("        ☝ One more thing to know:")
print("              🢡The ADMIN password is 'health'🢤")
print("              🢡The USER1 password is 'wellness'🢤")
print("              🢡password can be changed under 'INFORMATION' card🢤")
webbrowser.open(url)



	
#Making the necessary directories:
#make a new dir to expand healthdata into
#new_dir_name = 'Health_server'
#home_dir = Path.home()
#HS_path = os.path.join(str(home_dir), new_dir_name)
#subprocess.run(['mkdir', HS_path])
#making necessary subdirectories, #Health_files #upload, #ocr_files
#Health_files = 'Health_files'
#upload_dir = 'upload'
#ocr_files = 'ocr_files'
#Health_files = os.path.join(str(HS_path), Health_files)
#subprocess.run(['mkdir', Health_files])
#upload_dir = os.path.join(str(Health_files), upload_dir)
#ocr_files = os.path.join(str(Health_files), ocr_files)
#subprocess.run(['mkdir', upload_dir])
#subprocess.run(['mkdir', ocr_files]) 










