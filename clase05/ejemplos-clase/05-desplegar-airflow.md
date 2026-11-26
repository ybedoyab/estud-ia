# Desplegar

```powershell
.\scripts\preparar.ps1
.\scripts\iniciar.ps1
.\scripts\comprobar.ps1
```

`preparar` copia `.env.example` a `.env` si no existe, genera `FERNET_KEY` y escribe `config/simple_auth_passwords.json`.

`iniciar` migra la base y levanta los servicios.

`comprobar` pide `http://127.0.0.1:8080/api/v2/monitor/health`.

Apagar, sin borrar metadatos:

```powershell
.\scripts\detener.ps1
```

Borrar también la base local, a propósito:

```powershell
docker compose down -v
```

Eso no toca GCP.
