#!/bin/bash
set -euo pipefail
gcloud compute ssh estudia-airflow-clase03 --project=drafty-autopilot-fx --zone=southamerica-east1-a --tunnel-through-iap --command="cd /opt/estudia-clase03/airflow && sudo docker compose ps"
