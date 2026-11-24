$ErrorActionPreference = "Stop"
gcloud compute ssh estudia-airflow-clase03 --project=drafty-autopilot-fx --account=fastex.999@gmail.com --zone=southamerica-east1-a --tunnel-through-iap --command="sudo bash /opt/estudia-clase04/infra/start.sh"
