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
import shutil

# Label current dir and parent dir
HS_path = os.getcwd()
APP_dir = f"{HS_path}/install_module"

current_dir = f"{APP_dir}/Ibs_Module" #replace this and following code in new app
#current_dir=HS_path
# Build the source and destination file paths
source_file_path = os.path.join(current_dir, "Ibs_Module_script.js")
destination_file_path = os.path.join(HS_path, "static", "Ibs_Module_script.js")

def main():
    try:
        subprocess.run(["docker", "build", "-t", "darnahi_ibs_tracker", "."], cwd=current_dir)
        #docker build -t darnahi_weight_tracker .
        
        subprocess.run(["docker", "run", "-d", "--restart", "unless-stopped", "--network", "host", "--name", "darnahi_ibs_tracker", "-e", "OLLAMA_HOST=http://localhost:11434", "darnahi_ibs_tracker"])
        #docker run -d --restart unless-stopped --network host --name darnahi_weight_tracker -e OLLAMA_HOST=http://localhost:11434 darnahi_weight_tracker

        #write to static/Weight_Tracker_script.js
        shutil.copy(source_file_path, destination_file_path)
        print(f"File copied to {destination_file_path}")
    
    except subprocess.CalledProcessError as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

#write to static/Tailscale_script.js
#file_path = f'{HS_path}/static/'
#command3 = f"cp {current_dir}/Weight_Tracker_script.js {file_path}/Weight_Tracker_script.js"
#os.system(command3)
