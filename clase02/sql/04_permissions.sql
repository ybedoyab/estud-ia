-- Permisos de solo lectura. Ejecutar después de crear las vistas.

REVOKE ALL ON SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL SEQUENCES IN SCHEMA public FROM PUBLIC;
REVOKE ALL ON ALL FUNCTIONS IN SCHEMA public FROM PUBLIC;

REVOKE ALL ON SCHEMA curso FROM PUBLIC;
REVOKE ALL ON ALL TABLES IN SCHEMA curso FROM PUBLIC;

GRANT USAGE ON SCHEMA curso TO rol_estudiante;
GRANT SELECT ON ALL TABLES IN SCHEMA curso TO rol_estudiante;

ALTER DEFAULT PRIVILEGES IN SCHEMA curso
    GRANT SELECT ON TABLES TO rol_estudiante;

REVOKE INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
    ON ALL TABLES IN SCHEMA curso FROM PUBLIC;
REVOKE INSERT, UPDATE, DELETE, TRUNCATE, REFERENCES, TRIGGER
    ON ALL TABLES IN SCHEMA curso FROM rol_estudiante;

REVOKE TEMPORARY ON DATABASE retail_dwh FROM PUBLIC;
REVOKE TEMPORARY ON DATABASE retail_dwh FROM rol_estudiante;

CREATE SCHEMA IF NOT EXISTS pgbouncer;
REVOKE ALL ON SCHEMA pgbouncer FROM PUBLIC;

CREATE OR REPLACE FUNCTION pgbouncer.user_search(uname text)
RETURNS TABLE (usename name, passwd text)
LANGUAGE sql
SECURITY DEFINER
SET search_path = pg_catalog
AS $$
    SELECT rolname, rolpassword
    FROM pg_authid
    WHERE rolname = uname
      AND rolcanlogin
$$;

REVOKE ALL ON FUNCTION pgbouncer.user_search(text) FROM PUBLIC;

DO $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'pgbouncer_auth') THEN
        GRANT USAGE ON SCHEMA pgbouncer TO pgbouncer_auth;
        GRANT EXECUTE ON FUNCTION pgbouncer.user_search(text) TO pgbouncer_auth;
        GRANT CONNECT ON DATABASE retail_dwh TO pgbouncer_auth;
    END IF;
END
$$;

CREATE OR REPLACE FUNCTION public.estudia_block_student_ddl()
RETURNS event_trigger
LANGUAGE plpgsql
AS $$
BEGIN
    IF session_user LIKE 'estudiante%' THEN
        RAISE EXCEPTION 'operacion no permitida para cuentas de estudiante';
    END IF;
END;
$$;

REVOKE ALL ON FUNCTION public.estudia_block_student_ddl() FROM PUBLIC;

DROP EVENT TRIGGER IF EXISTS estudia_block_student_ddl;
CREATE EVENT TRIGGER estudia_block_student_ddl
    ON ddl_command_start
    EXECUTE FUNCTION public.estudia_block_student_ddl();
