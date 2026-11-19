#!/bin/bash
set -euo pipefail
gcloud compute ssh estudia-airflow-clase03 --project=drafty-autopilot-fx --zone=southamerica-east1-a --tunnel-through-iap --command="cd /opt/estudia-clase03/airflow && sudo docker compose stop" || true
gcloud compute instances stop estudia-airflow-clase03 --project=drafty-autopilot-fx --zone=southamerica-east1-a
echo "VM detenida. El disco, los DAG, los reportes y la IP reservada se conservan."
