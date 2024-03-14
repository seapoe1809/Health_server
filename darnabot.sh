#!/bin/bash
cd /Health_server/darnabot
source llmvenv/bin/activate
# Set the environment variable HF_HOME
export HF_HOME=/darnabot/cache/hub
export HUGGINGFACE_HUB_CACHE=/darnabot/cache/huggingface/hub
export TRANSFORMERS_CACHE=/darnabot/cache/
nohup python3 darnabot.py &> darnabot.log &
