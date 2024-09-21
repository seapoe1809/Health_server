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

#dockerfile
FROM python:3.10

# Set the working directory in the container
WORKDIR /workspace

# Install the necessary Python packages
# Install virtualenv
RUN pip install --upgrade pip && \
    pip install virtualenv && \
    python -m virtualenv venv

RUN python -m virtualenv venv

RUN . /workspace/venv/bin/activate && \
    pip install pip-tools pandas gradio ollama plotly



# Copy the current directory contents into the container at /workspace
ADD vacc_mod.py ./
#adminADD /uploads ./
RUN mkdir uploads
COPY uploads ./uploads

# Make port 3020 available to the world outside this container
EXPOSE 3022

# Run main.py when the container launches
CMD [ "/bin/bash", "-c", "source /workspace/venv/bin/activate && python vacc_mod.py" ]

#docker build -t darnahi_immunization_tracker .


#docker run -d --restart unless-stopped --network host --name darnahi_immunization_tracker -e OLLAMA_HOST=http://localhost:11434 darnahi_immunization_tracker




