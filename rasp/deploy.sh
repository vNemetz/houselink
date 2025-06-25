#!/bin/bash

echo "Deploying files to Raspberry Pi..."

# Copy files to Raspberry Pi
scp /home/vnemetz/Documentos/oficinas41/rasp/servo_controller.py rasp@192.168.198.84:/home/rasp/servo/
scp /home/vnemetz/Documentos/oficinas41/rasp/requirements.txt rasp@192.168.198.84:/home/rasp/servo/
scp /home/vnemetz/Documentos/oficinas41/rasp/servo-controller.service rasp@192.168.198.84:/home/rasp/servo/

# SSH into Raspberry Pi and update the service
ssh rasp@192.168.198.84 << 'EOF'
    echo "Installing dependencies..."
    cd /home/rasp/servo
    source venv/bin/activate
    pip install -r requirements.txt

    echo "Updating service configuration..."
    # Move service file to systemd directory
    sudo cp servo-controller.service /etc/systemd/system/

    # Reload systemd and restart the service
    sudo systemctl daemon-reload
    sudo systemctl restart servo-controller
    
    # Show status
    echo "Service status:"
    sudo systemctl status servo-controller
EOF

echo "Deployment complete!"