# Instalar Docker Desktop

Página oficial: https://www.docker.com/products/docker-desktop/

Windows:

1. Virtualización activa.
2. WSL2. Si falta: `wsl --install` y reiniciar.
3. Instalar Docker Desktop y abrirlo.
4. Comprobar:

```powershell
docker --version
docker compose version
docker run --rm hello-world
```

Linux: Docker Engine y el plugin Compose del repositorio de la distribución, no un script suelto. macOS: Docker Desktop para el chip del equipo.

Memoria: 8 GB en el equipo es lo cómodo. Asigna al menos 4 GB a Docker Desktop. El tamaño exacto de la descarga no se midió en la máquina de preparación porque el motor de Docker estaba apagado. La imagen de Airflow 3.4 y Postgres 16.6 son el grueso.

VS Code no hace falta. Sirve cualquier editor para cambiar los `COMPLETA`.
