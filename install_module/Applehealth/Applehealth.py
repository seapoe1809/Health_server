#will run to install the docker container and then replace the js module to allow opening port
import os
import subprocess
import docker

# Label current dir and parent dir
HS_path = os.getcwd()
APP_dir = f"{HS_path}/install_module"

current_dir = f"{APP_dir}/Applehealth" #replace this and following code in new app
upload_dir =f"{HS_path}/Health_files/upload"

#image = ""
#Darna.hi will use third party https://github.com/k0rventen/apple-health-grafana to visualize the apple health data. Cloning repository in the current directory and modifying the volume: of yml file...
grafana_repository='https://github.com/k0rventen/apple-health-grafana'

try:
    result = subprocess.run(['git', 'clone', grafana_repository], cwd=HS_path)
    if result.returncode == 0:
        print("Repository cloned...")
    else:
        print("Failed to clone the repository :(")
except Exception as e:
    print(f"An error occurred while cloning the repository: {e}")

# Write volume in docker-compose file for apple-health-grafana
# Modify the volume in docker-compose.yml
volume = f'    - {upload_dir}/export.zip:/export.zip'
grafana_docker = f'{HS_path}/apple-health-grafana/docker-compose.yml'

try:
    with open(grafana_docker, 'r') as file:
        lines = file.readlines()

    if len(lines) >= 1:
        lines[-4] = volume

    with open(grafana_docker, 'w') as file:
        file.writelines(lines)
except FileNotFoundError:
    print(f"The file {grafana_docker} was not found.")
except Exception as e:
    print(f"An error occurred while modifying the docker-compose file: {e}")

#write to static/applehealth_script.js
file_path = f'{HS_path}/static/'
command3 = f"cp {current_dir}/Applehealth_script.js {file_path}/Applehealth_script.js"
os.system(command3)
