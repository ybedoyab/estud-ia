"""Bitácora JSON. No registra contraseñas, tokens ni cuerpos de login."""

import json
import logging
import sys


class _Json(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        payload = {
            "nivel": record.levelname,
            "mensaje": record.getMessage(),
        }
        datos = getattr(record, "datos", None)
        if isinstance(datos, dict):
            payload.update(datos)
        return json.dumps(payload, ensure_ascii=False, default=str)


def configurar() -> logging.Logger:
    logger = logging.getLogger("estudia.clase04")
    if logger.handlers:
        return logger
    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(_Json())
    logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    return logger


bitacora = configurar()
