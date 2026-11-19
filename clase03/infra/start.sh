#!/bin/bash
set -euo pipefail
gcloud compute instances start estudia-airflow-clase03 --project=drafty-autopilot-fx --zone=southamerica-east1-a
gcloud compute ssh estudia-airflow-clase03 --project=drafty-autopilot-fx --zone=southamerica-east1-a --tunnel-through-iap --command="cd /opt/estudia-clase03/airflow && sudo docker compose up -d"
echo "Airflow y la API vuelven a arrancar. Los DAG de estudiantes siguen pausados hasta que cada quien vuelva a publicar."
