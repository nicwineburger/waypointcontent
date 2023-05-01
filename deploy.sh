#!/bin/bash
cd /root/waypointcontent
source venv/bin/activate
pip install -r requirements.txt
deactivate
sudo systemctl restart waypointcontent

