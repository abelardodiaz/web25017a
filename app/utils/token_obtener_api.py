# app/utils/token_obtener_api.py
import requests
from datetime import datetime, timedelta, timezone
from app import db
from app.models import SyscomCredential
from sqlalchemy.exc import SQLAlchemyError
import logging

logger = logging.getLogger(__name__)

TOKEN_URL = "https://developers.syscom.mx/oauth/token"
def request_token(cred: SyscomCredential) -> bool:
    payload = {
        "client_id": cred.client_id.strip(),
        "client_secret": cred.client_secret.strip(),
        "grant_type": "client_credentials",
    }
    try:
        logger.info("Solicitando token a SYSCOM…")
        resp = requests.post(
            TOKEN_URL,
            headers={"Content-Type": "application/json",
                     "Accept": "application/json"},
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()

        if "access_token" not in data:
            logger.error(f"Respuesta sin token: {data}")
            return False

        cred.token = data["access_token"]
        cred.expires_at = datetime.now(timezone.utc) + timedelta(
            seconds=int(data.get("expires_in", 0))
        )
        db.session.commit()
        logger.info(f"Token guardado. Expira en {cred.expires_at.isoformat()}")
        return True

    except requests.RequestException as e:
        logger.exception(f"Error de conexión: {e}")
    except Exception:
        logger.exception("Error inesperado")
    return False