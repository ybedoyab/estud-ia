#!/bin/bash
# Copia el codigo de esta carpeta a la VM y vuelve a levantar los contenedores.
# No rota secretos: remote_bootstrap.sh solo los crea si aun no existen.
set -euo pipefail
gcloud compute scp --recurse --tunnel-through-iap --project=drafty-autopilot-fx --zone=southamerica-east1-a \
  "$(dirname "$0")/../airflow" "$(dirname "$0")/../api" "$(dirname "$0")/../infra" \
  estudia-airflow-clase03:/tmp/clase03-deploy
gcloud compute ssh estudia-airflow-clase03 --project=drafty-autopilot-fx --zone=southamerica-east1-a --tunnel-through-iap --command="sudo cp -a /tmp/clase03-deploy/airflow/. /opt/estudia-clase03/airflow/ && sudo cp -a /tmp/clase03-deploy/api/. /opt/estudia-clase03/api/ && sudo cp -a /tmp/clase03-deploy/infra/. /opt/estudia-clase03/infra/ && sudo bash /opt/estudia-clase03/infra/remote_bootstrap.sh"
