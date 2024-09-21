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
#will run to install the docker container and then replace the js module to allow opening port

import os
import subprocess
import sys

# Label current dir and parent dir
HS_path = os.getcwd()
APP_dir = f"{HS_path}/install_module"

if sys.version_info < (3, 0):
    print("This script requires Python 3 or higher!")
    sys.exit(1)

current_dir = f"{APP_dir}/Dock"  # replace this and the following code in new app

try:
    result1 = subprocess.run(['docker', 'volume', 'create', 'yacht'], cwd=HS_path, check=True)
    result2 = subprocess.run([
        'docker', 'run', '-d', '-p', '3009:8000',
        '-v', '/var/run/docker.sock:/var/run/docker.sock',
        '-v', 'yacht:/config', '--name', 'yacht', 'selfhostedpro/yacht'
    ], cwd=HS_path, check=True)
    
    print("Installed Yacht, your Docker Dock")
except subprocess.CalledProcessError:
    print("Failed to create Dock")
except Exception as e:
    print(f"An error occurred while creating Dock: {e}")

# write to static/dock_script.js
file_path = f'{HS_path}/static/'
command3 = f"cp {current_dir}/Dock_script.js {file_path}/Dock_script.js"
os.system(command3)

