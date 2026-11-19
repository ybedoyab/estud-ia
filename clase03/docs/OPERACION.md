# Operación

Desde la máquina del docente, con `gcloud` ya autenticado como `fastex.999@gmail.com`.

## Estado

```bash
gcloud compute ssh estudia-airflow-clase03 --project=drafty-autopilot-fx --zone=southamerica-east1-a --tunnel-through-iap --command="cd /opt/estudia-clase03/airflow && sudo docker compose ps"
```

## Encender

```bash
gcloud compute instances start estudia-airflow-clase03 --project=drafty-autopilot-fx --zone=southamerica-east1-a
gcloud compute ssh estudia-airflow-clase03 --project=drafty-autopilot-fx --zone=southamerica-east1-a --tunnel-through-iap --command="cd /opt/estudia-clase03/airflow && sudo docker compose up -d"
```

Los DAG estudiantiles no se reactivan solos. Cada estudiante vuelve a publicar, o se quita la pausa desde Airflow.

## Pausar los DAG de estudiantes

En la VM:

```bash
cd /opt/estudia-clase03/airflow
sudo docker compose exec -T fastapi python -c "import os,httpx; print(httpx.post('http://127.0.0.1:8000/admin/pause-all', headers={'X-Admin-Token': os.environ['ESTUDIA_ADMIN_TOKEN']}).status_code)"
```

Hay un temporizador systemd, `estudia-pausa-dags.timer`, que llama a ese endpoint a las 21:00 de Bogotá. No apaga la VM y no corta una tarea que ya empezó: solo impide corridas nuevas.

## Detener Airflow y la VM

```bash
gcloud compute ssh estudia-airflow-clase03 --project=drafty-autopilot-fx --zone=southamerica-east1-a --tunnel-through-iap --command="cd /opt/estudia-clase03/airflow && sudo docker compose stop"
gcloud compute instances stop estudia-airflow-clase03 --project=drafty-autopilot-fx --zone=southamerica-east1-a
```

`docker compose stop` no borra volúmenes. Al encender de nuevo siguen los DAG, el historial, los CSV y los logs.

Con la VM apagada se sigue cobrando el disco de 30 GB y la IP reservada `34.95.210.33`. No se cobra el cómputo. Para dejar de cobrar la IP habría que borrarla, y las URL de la clase cambiarían.

## Error de demostración

```bash
cd /opt/estudia-clase03/airflow
sudo docker compose exec airflow-apiserver airflow variables set estudia_demo_forzar_error 1
sudo docker compose exec airflow-apiserver airflow variables set estudia_demo_forzar_error 0
```

## Costo orientativo

La VM `e2-standard-2` en São Paulo sale cerca de 0,11 USD por hora, unos 350 COP. El disco y la IP, con la máquina apagada, siguen en la factura del mes: del orden de 20 000 COP si la IP sigue reservada. Conviene detener la VM al terminar la clase.
