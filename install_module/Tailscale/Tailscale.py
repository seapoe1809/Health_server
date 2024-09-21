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
import docker

# Label current dir and parent dir
HS_path = os.getcwd()
APP_dir = f"{HS_path}/install_module"

current_dir = f"{APP_dir}/Tailscale" #replace this and following code in new app


image = "tailscale/tailscale:v1.40.1@sha256:08dd1f465d6e96192b36c10f4366b3988bc6ad29f7b264bd020c1762ee325305"

# Pull the Docker image
client = docker.from_env()
client.images.pull(image)

# Run the Docker container with port mappings
container = client.containers.run(
    image,
    network_mode='host',
    volumes={HS_path: {'bind': '/var/lib', 'mode': 'rw'}},
    restart_policy={"Name": "always"},
    detach=True,
    command="sh -c 'tailscale web --listen 0.0.0.0:8240 & exec tailscaled --tun=userspace-networking'"
)

#write to static/Tailscale_script.js
file_path = f'{HS_path}/static/'
command3 = f"cp {current_dir}/Tailscale_script.js {file_path}/Tailscale_script.js"
os.system(command3)
