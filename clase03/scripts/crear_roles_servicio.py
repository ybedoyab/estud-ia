"""Crea el rol de lectura de Airflow y las cuentas de prueba. No imprime contraseñas."""

import secrets
import subprocess
from pathlib import Path

KEY = str(Path.home() / ".ssh" / "google_compute_engine")
KNOWN_AIR = str(Path.home() / "AppData/Local/Temp/estudia_airflow_known")
KNOWN_PG = str(Path.home() / "AppData/Local/Temp/estudia_known_hosts")


def ssh(port, known, remote, data=None):
    command = [
        "ssh", "-i", KEY, "-p", str(port),
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", f"UserKnownHostsFile={known}",
        "yulcr@127.0.0.1", remote,
    ]
    result = subprocess.run(command, input=data, text=True, capture_output=True)
    if result.returncode != 0:
        raise SystemExit(result.stderr[-800:])
    return result.stdout


def main():
    lectura = ssh(2223, KNOWN_AIR, "sudo cat /root/estudia-clase03/airflow_lectura.password").strip()
    cuentas = {"airflow_lectura": lectura}
    for numero in range(80, 100):
        cuentas[f"estudiante{numero:02d}"] = secrets.token_urlsafe(18)
    csv = ["usuario,password"]
    csv.extend(f"{usuario},{password}" for usuario, password in cuentas.items() if usuario != "airflow_lectura")
    ssh(
        2223,
        KNOWN_AIR,
        "sudo tee /root/estudia-clase03/cuentas_prueba.csv >/dev/null && sudo chmod 600 /root/estudia-clase03/cuentas_prueba.csv",
        "\n".join(csv) + "\n",
    )
    bloques = []
    for usuario, password in cuentas.items():
        limite = 8 if usuario == "airflow_lectura" else 2
        password_sql = password.replace("'", "''")
        bloques.append(
            f"""
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{usuario}') THEN
    CREATE ROLE {usuario} LOGIN PASSWORD '{password_sql}' NOSUPERUSER NOCREATEDB NOCREATEROLE
      NOREPLICATION NOBYPASSRLS INHERIT CONNECTION LIMIT {limite};
  ELSE
    ALTER ROLE {usuario} WITH LOGIN PASSWORD '{password_sql}' CONNECTION LIMIT {limite};
  END IF;
END
$$;
GRANT CONNECT ON DATABASE retail_dwh TO {usuario};
GRANT rol_estudiante TO {usuario};
ALTER ROLE {usuario} SET default_transaction_read_only = on;
ALTER ROLE {usuario} SET statement_timeout = '15s';
ALTER ROLE {usuario} SET search_path = curso;
"""
        )
    sql = "\n".join(bloques) + "\nSELECT count(*) AS roles_listos FROM pg_roles WHERE rolname = 'airflow_lectura' OR rolname ~ '^estudiante(8|9)[0-9]$';\n"
    salida = ssh(2222, KNOWN_PG, "sudo -u postgres psql -d retail_dwh -v ON_ERROR_STOP=1", sql)
    for linea in salida.splitlines():
        if "roles_listos" in linea or linea.strip().isdigit():
            print(linea)


if __name__ == "__main__":
    main()
