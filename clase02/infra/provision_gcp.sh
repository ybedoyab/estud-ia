#!/bin/bash
# Recursos de Compute Engine para el laboratorio. Idempotente solo en el primer alta:
# si el recurso ya existe, gcloud fallará y hay que reutilizarlo, no duplicarlo.
set -euo pipefail

PROJECT_ID="${PROJECT_ID:-drafty-autopilot-fx}"
REGION="${REGION:-southamerica-east1}"
ZONE="${ZONE:-southamerica-east1-a}"
VM_NAME="${VM_NAME:-estudia-postgres-lab}"
ADDRESS_NAME="${ADDRESS_NAME:-estudia-postgres-lab-ip}"
NETWORK="${NETWORK:-estudia-lab-vpc}"
SUBNET="${SUBNET:-estudia-lab-subnet}"

gcloud config set account "${GCLOUD_ACCOUNT:-fastex.999@gmail.com}"
gcloud config set project "$PROJECT_ID"
gcloud services enable compute.googleapis.com iap.googleapis.com --project="$PROJECT_ID" --quiet

gcloud compute networks create "$NETWORK" \
  --project="$PROJECT_ID" \
  --subnet-mode=custom \
  --description="VPC dedicada al laboratorio PostgreSQL de EstudIA clase02"

gcloud compute networks subnets create "$SUBNET" \
  --project="$PROJECT_ID" \
  --network="$NETWORK" \
  --region="$REGION" \
  --range=10.20.0.0/24 \
  --description="Subred del laboratorio PostgreSQL EstudIA"

gcloud compute firewall-rules create estudia-lab-allow-pgbouncer \
  --project="$PROJECT_ID" \
  --network="$NETWORK" \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:6432 \
  --source-ranges=0.0.0.0/0 \
  --target-tags=estudia-postgres-lab \
  --description="EstudIA clase02: unico puerto SQL de estudiantes (PgBouncer TLS)"

gcloud compute firewall-rules create estudia-lab-allow-iap-ssh \
  --project="$PROJECT_ID" \
  --network="$NETWORK" \
  --direction=INGRESS \
  --action=ALLOW \
  --rules=tcp:22 \
  --source-ranges=35.235.240.0/20 \
  --target-tags=estudia-postgres-lab \
  --description="SSH solo desde Identity-Aware Proxy, no desde Internet"

gcloud compute addresses create "$ADDRESS_NAME" \
  --project="$PROJECT_ID" \
  --region="$REGION" \
  --network-tier=PREMIUM \
  --description="IP estatica del laboratorio PostgreSQL EstudIA clase02"

IP="$(gcloud compute addresses describe "$ADDRESS_NAME" --project="$PROJECT_ID" --region="$REGION" --format='value(address)')"

gcloud compute instances create "$VM_NAME" \
  --project="$PROJECT_ID" \
  --zone="$ZONE" \
  --machine-type=e2-medium \
  --image-family=ubuntu-2404-lts-amd64 \
  --image-project=ubuntu-os-cloud \
  --boot-disk-size=20GB \
  --boot-disk-type=pd-balanced \
  --boot-disk-device-name="$VM_NAME" \
  --network="$NETWORK" \
  --subnet="$SUBNET" \
  --address="$IP" \
  --tags=estudia-postgres-lab \
  --labels=app=estudia,component=postgres-lab,course=clase02,environment=lab \
  --scopes="https://www.googleapis.com/auth/logging.write,https://www.googleapis.com/auth/monitoring.write" \
  --shielded-vtpm \
  --shielded-integrity-monitoring \
  --deletion-protection \
  --metadata=enable-oslogin=FALSE,lab=estudia-clase02 \
  --maintenance-policy=MIGRATE

echo "PUBLIC_IP=$IP"
echo "PROJECT=$PROJECT_ID"
echo "ZONE=$ZONE"
