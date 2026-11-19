#!/bin/bash
# Crea la VM de Airflow en el proyecto ya existente. No toca la VM de PostgreSQL.
set -euo pipefail
PROJECT_ID="${PROJECT_ID:-drafty-autopilot-fx}"
REGION="${REGION:-southamerica-east1}"
ZONE="${ZONE:-southamerica-east1-a}"
gcloud config set account "${GCLOUD_ACCOUNT:-fastex.999@gmail.com}"
gcloud config set project "$PROJECT_ID"
gcloud compute addresses create estudia-airflow-clase03-ip \
  --project="$PROJECT_ID" --region="$REGION" --network-tier=PREMIUM
gcloud compute firewall-rules create estudia-airflow-allow-web \
  --project="$PROJECT_ID" --network=estudia-lab-vpc \
  --direction=INGRESS --action=ALLOW --rules=tcp:80,tcp:443 \
  --source-ranges=0.0.0.0/0 --target-tags=estudia-airflow
gcloud compute firewall-rules create estudia-airflow-allow-iap-ssh \
  --project="$PROJECT_ID" --network=estudia-lab-vpc \
  --direction=INGRESS --action=ALLOW --rules=tcp:22 \
  --source-ranges=35.235.240.0/20 --target-tags=estudia-airflow
IP="$(gcloud compute addresses describe estudia-airflow-clase03-ip --project="$PROJECT_ID" --region="$REGION" --format='value(address)')"
gcloud compute instances create estudia-airflow-clase03 \
  --project="$PROJECT_ID" --zone="$ZONE" --machine-type=e2-standard-2 \
  --image-family=ubuntu-2404-lts-amd64 --image-project=ubuntu-os-cloud \
  --boot-disk-size=30GB --boot-disk-type=pd-balanced \
  --network=estudia-lab-vpc --subnet=estudia-lab-subnet --address="$IP" \
  --tags=estudia-airflow \
  --labels=app=estudia,component=airflow,course=clase03,environment=lab \
  --scopes="https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write" \
  --metadata=enable-oslogin=FALSE --deletion-protection
echo "PUBLIC_IP=$IP"
