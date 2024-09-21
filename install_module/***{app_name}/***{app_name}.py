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

#will run to install the docker container and then replace the js module to allow opening port; replace *** with relevant variables
import os
import docker

# Label current dir and parent dir
HS_path = os.getcwd()
APP_dir = f"{HS_path}/install_module"
current_dir = f"{APP_dir}/APP"


image = "***"

# Pull the Docker image
client = docker.from_env()
client.images.pull(image)

# Run the Docker container with port mappings
container = client.containers.run(
    image,
    ports={"***": "***"},
    volumes={HS_path: {'bind': '/var/lib', 'mode': 'rw'}},
    restart_policy={"Name": "on-failure", "MaximumRetryCount": 5},
    detach=True,
    command="***"
)

#write to static/tail_script.js
file_path = f'{HS_path}/static/'
command3 = f"cp {current_dir}/***_script.js {file_path}/***_script.js"
print(command3)
print(os.path.exists(f'{current_dir}/***_script.js'))
os.system(command3)
