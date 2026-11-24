#!/bin/bash
set -euo pipefail
cd /opt/estudia-clase04/infra
sudo docker compose start
sudo docker compose ps
