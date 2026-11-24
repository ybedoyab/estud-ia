#!/usr/bin/env python3
"""Crea la cuenta técnica y las cuentas sintéticas 46-90. No imprime contraseñas."""

import csv
import os
import pwd
import secrets
import subprocess
from pathlib import Path

DESTINO = Path("/root/estudia-clase04/cuentas.csv")
COPIA = Path("/home/yulcr/estudia-clase04-cuentas.csv")


def sql_literal(valor: str) -> str:
    return "'" + valor.replace("'", "''") + "'"


def cargar() -> list[tuple[str, str]]:
    if DESTINO.exists():
        with DESTINO.open(encoding="utf-8", newline="") as handle:
            return [(fila["usuario"], fila["password"]) for fila in csv.DictReader(handle)]
    cuentas = [("clase04_lectura", secrets.token_urlsafe(24))]
    cuentas.extend((f"estudiante{numero:02d}", secrets.token_urlsafe(18)) for numero in range(46, 91))
    DESTINO.parent.mkdir(parents=True, exist_ok=True)
    with DESTINO.open("w", encoding="utf-8", newline="") as handle:
        escritor = csv.writer(handle)
        escritor.writerow(["usuario", "password"])
        escritor.writerows(cuentas)
    DESTINO.chmod(0o600)
    return cuentas


def aplicar(cuentas: list[tuple[str, str]]) -> None:
    bloques = []
    for usuario, password in cuentas:
        limite = 12 if usuario == "clase04_lectura" else 3
        bloques.append(
            f"""
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{usuario}') THEN
    CREATE ROLE {usuario} LOGIN PASSWORD {sql_literal(password)}
      NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS INHERIT
      CONNECTION LIMIT {limite};
  ELSE
    ALTER ROLE {usuario} WITH LOGIN PASSWORD {sql_literal(password)}
      NOSUPERUSER NOCREATEDB NOCREATEROLE NOREPLICATION NOBYPASSRLS INHERIT
      CONNECTION LIMIT {limite};
  END IF;
END
$$;
GRANT CONNECT ON DATABASE retail_dwh TO {usuario};
GRANT rol_estudiante TO {usuario};
ALTER ROLE {usuario} SET default_transaction_read_only = on;
ALTER ROLE {usuario} SET statement_timeout = '8s';
ALTER ROLE {usuario} SET search_path = curso;
"""
        )
    bloques.append(
        """
SELECT rolname, rolsuper, rolcreaterole, rolcanlogin, rolconnlimit
FROM pg_roles
WHERE rolname = 'clase04_lectura';
SELECT count(*) AS sinteticas
FROM pg_roles
WHERE rolname ~ '^estudiante(4[6-9]|[5-8][0-9]|90)$';
"""
    )
    resultado = subprocess.run(
        ["sudo", "-u", "postgres", "psql", "-d", "retail_dwh", "-v", "ON_ERROR_STOP=1"],
        input="\n".join(bloques),
        text=True,
        capture_output=True,
        check=False,
    )
    if resultado.returncode != 0:
        DESTINO.parent.mkdir(parents=True, exist_ok=True)
        (DESTINO.parent / "psql.err").write_text(resultado.stderr, encoding="utf-8")
        print("psql_fallo")
        raise SystemExit(resultado.returncode)
    for linea in resultado.stdout.splitlines():
        if "clase04_lectura" in linea or "sinteticas" in linea or linea.strip().isdigit():
            print(linea)


def publicar(cuentas: list[tuple[str, str]]) -> None:
    with COPIA.open("w", encoding="utf-8", newline="") as handle:
        escritor = csv.writer(handle)
        escritor.writerow(["usuario", "password"])
        escritor.writerows(cuentas)
    COPIA.chmod(0o600)
    usuario = pwd.getpwnam("yulcr")
    os.chown(COPIA, usuario.pw_uid, usuario.pw_gid)


if __name__ == "__main__":
    pares = cargar()
    aplicar(pares)
    publicar(pares)
    print(f"cuentas={len(pares)}")
