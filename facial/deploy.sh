#!/bin/bash

echo "Deploying recognition.py to Raspberry Pi..."

# Define the Raspberry Pi's IP and target directory
RASPBERRY_PI_IP="192.168.198.84"
TARGET_DIR="/home/rasp/Facial-Recognition-in-Python/Recognition"

# Create the target directory on the Raspberry Pi
ssh rasp@$RASPBERRY_PI_IP "mkdir -p $TARGET_DIR"

# Copy recognition.py to Raspberry Pi
scp /home/vnemetz/Documentos/oficinas41/facial/recognition.py rasp@$RASPBERRY_PI_IP:$TARGET_DIR

echo "Deployment complete!"