#!/bin/bash
set -euo pipefail
cd /opt/estudia-clase04/infra
sudo docker compose ps
sudo docker stats --no-stream --format '{{.Name}} {{.CPUPerc}} {{.MemUsage}}' | grep clase04 || true
