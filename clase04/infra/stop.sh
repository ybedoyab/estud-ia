#!/bin/bash
set -euo pipefail
cd /opt/estudia-clase04/infra
sudo docker compose stop
sudo docker compose ps
