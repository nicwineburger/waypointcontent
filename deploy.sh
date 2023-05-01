#!/bin/bash
cd /root/waypointcontent
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart waypointcontent

