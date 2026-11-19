-- Roles base del laboratorio. No contiene contraseñas.
-- Las cuentas de servicio con LOGIN se crean en scripts/create_service_roles.py
-- y las de estudiantes en scripts/create_students.py.

DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'rol_estudiante') THEN
        CREATE ROLE rol_estudiante
            NOLOGIN
            NOSUPERUSER
            NOCREATEDB
            NOCREATEROLE
            NOREPLICATION
            NOBYPASSRLS
            INHERIT;
    END IF;
END
$$;

ALTER ROLE rol_estudiante
    NOSUPERUSER
    NOCREATEDB
    NOCREATEROLE
    NOREPLICATION
    NOBYPASSRLS
    INHERIT;

COMMENT ON ROLE rol_estudiante IS
    'Grupo de solo lectura para estudiantes de EstudIA. Sin LOGIN.';

-- Privilegios peligrosos que PostgreSQL concede a PUBLIC por defecto.
REVOKE ALL ON DATABASE retail_dwh FROM PUBLIC;
REVOKE TEMPORARY ON DATABASE retail_dwh FROM PUBLIC;
REVOKE CREATE ON DATABASE retail_dwh FROM PUBLIC;
REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE CREATE ON SCHEMA public FROM PUBLIC;

REVOKE CONNECT ON DATABASE postgres FROM PUBLIC;

GRANT CONNECT ON DATABASE retail_dwh TO rol_estudiante;
GRANT TEMPORARY ON DATABASE retail_dwh TO postgres;
