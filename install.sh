#!/bin/bash

# Define variables
REPO_URL="https://github.com/Romaxa55/CameraMonitorFB.git"   # Replace with your repository URL
SERVICE_NAME="dvrfbdisplay"
INSTALL_DIR="/opt/$SERVICE_NAME"

# Update and install dependencies
sudo apt update && sudo apt install -y python3 python3-venv git

# Create installation directory
sudo mkdir -p "$INSTALL_DIR"
sudo chown $USER:$USER "$INSTALL_DIR"

# Remove exist dir
rm -rf $INSTALL_DIR

# Clone the repository
echo "Cloning project from $REPO_URL..."
git clone "$REPO_URL" "$INSTALL_DIR"

# Create Python virtual environment
echo "Setting up virtual environment..."
python3 -m venv "$INSTALL_DIR/venv"
source "$INSTALL_DIR/venv/bin/activate"
pip install -r "$INSTALL_DIR/requirements.txt"

# Define systemd service file
SERVICE_FILE="/etc/systemd/system/$SERVICE_NAME.service"
sudo bash -c "cat > $SERVICE_FILE" << EOL
[Unit]
Description=DVRFBDisplay - Real-time Camera Monitoring on TV via fbdev
After=network.target

[Service]
ExecStart=$INSTALL_DIR/venv/bin/python3 $INSTALL_DIR/main.py
WorkingDirectory=$INSTALL_DIR
Restart=always
User=$USER
Environment=DISPLAY=:0
StandardOutput=inherit
StandardError=inherit

# Grant permissions to access /dev/fb0 if needed
PermissionsStartOnly=true
ExecStartPre=/bin/chmod 666 /dev/fb0

[Install]
WantedBy=multi-user.target
EOL

# Set permissions and reload systemd
echo "Configuring service..."
sudo chmod 644 "$SERVICE_FILE"
sudo systemctl daemon-reload
sudo systemctl enable "$SERVICE_NAME"

# Start the service
echo "Starting service..."
sudo systemctl start "$SERVICE_NAME"

# Check service status
echo "Service status:"
sudo systemctl status "$SERVICE_NAME"
