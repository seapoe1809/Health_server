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
import shutil

# Label current dir and parent dir
HS_path = os.getcwd()
APP_dir = f"{HS_path}/install_module"

current_dir = f"{APP_dir}/Strep_Module" #replace this and following code in new app
#current_dir=HS_path
# Build the source and destination file paths
source_file_path = os.path.join(current_dir, "Strep_Module_script.js")
destination_file_path = os.path.join(HS_path, "static", "Strep_Module_script.js")

def main():
    try:
        subprocess.run(["docker", "build", "-t", "darnahi_strep_module", "."], cwd=current_dir)
        
        subprocess.run(["docker", "run", "-d", "--restart", "unless-stopped", "--network", "host", "--name", "darnahi_strep_module", "-e", "OLLAMA_HOST=http://localhost:11434", "darnahi_strep_module"])
        #docker run -d --restart unless-stopped --network host --name darnahi_*** -e OLLAMA_HOST=http://localhost:11434 darnahi_***

        #write to static/Weight_Tracker_script.js
        shutil.copy(source_file_path, destination_file_path)
        print(f"File copied to {destination_file_path}")
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

