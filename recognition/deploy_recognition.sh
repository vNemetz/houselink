#!/bin/bash

echo "Deploying face recognition system to Raspberry Pi..."

scp recognition.py rasp@192.168.198.84:/home/rasp/servo/
scp recognition.service rasp@192.168.198.84:/home/rasp/servo/
scp recognition_requirements.txt rasp@192.168.198.84:/home/rasp/servo/

scp haarcascade_frontalface_default.xml rasp@192.168.198.84:/home/rasp/servo/
scp -r face_db rasp@192.168.198.84:/home/rasp/servo/



# Configurar ambiente na Raspberry Pi
ssh rasp@192.168.198.84 << 'EOF'
    echo "Installing dependencies..."
    cd /home/rasp/servo
    source venv/bin/activate

    #Se já estiver instalado o OpenCV não precisa desta linha
    sudo apt-get install -y python3-opencv
    pip install -r recognition_requirements.txt

    echo "Configuring service..."
    sudo cp face-recognition.service /etc/systemd/system/

    # Reload systemd and restart the service
    sudo systemctl daemon-reload
    sudo systemctl enable face-recognition
    sudo systemctl restart face-recognition
    
    echo "Service status:"
    sudo systemctl status face-recognition
EOF

echo "Deployment complete!"