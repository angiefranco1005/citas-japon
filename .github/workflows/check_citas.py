"""
Vigilante de citas - Embajada de Japón en Colombia (visa de corta estadía)
----------------------------------------------------------------------------
Revisa la tabla de horarios disponibles en:
https://embjpcol.rsvsys.jp/reservations/calendar

Si encuentra un horario con cupo suficiente para PERSONAS_REQUERIDAS
personas, envía un mensaje de Telegram usando CallMeBot (gratis).

Configuración necesaria (variables de entorno o edítalas abajo):
  - TELEGRAM_USER : tu usuario de Telegram, ej: @angiefranco
"""

import os
import re
import sys
import requests
from datetime import datetime

# ---------- CONFIGURACIÓN ----------
URL = "https://embjpcol.rsvsys.jp/reservations/calendar"
PERSONAS_REQUERIDAS = 2  # cuántos cupos necesitas en el mismo horario

TELEGRAM_USER = os.environ.get("TELEGRAM_USER", "@TU_USUARIO_AQUI")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "es-CO,es;q=0.9",
}


def enviar_telegram(mensaje: str):
    """Envía un mensaje de Telegram usando CallMeBot."""
    url = "https://api.callmebot.com/text.php"
    params = {
        "user": TELEGRAM_USER,
        "text": mensaje,
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        print(f"[Telegram] status={r.status_code} body={r.text[:200]}")
    except Exception as e:
        print(f"[Telegram] ERROR enviando mensaje: {e}")


def revisar_calendario():
    session = requests.Session()
    resp = session.get(URL, headers=HEADERS, timeout=20)
    resp.raise_for_status()
    html = resp.text

    # Busca patrones tipo: fecha (MM/DD) + hora + 残N件
    # La tabla real usa estructura HTML; aquí buscamos el patrón de texto
    # "残X件" (X = número de cupos restantes) que aparece junto a cada celda.
    filas = re.findall(r"残\*?(\d+)件", html)

    cupos_disponibles = [int(n) for n in filas if int(n) >= PERSONAS_REQUERIDAS]

    if cupos_disponibles:
        mensaje = (
            f"🇯🇵 ¡Hay cupo disponible para {PERSONAS_REQUERIDAS} personas "
            f"en la cita de visa de Japón! Entra YA: {URL}"
        )
        print(mensaje)
        enviar_telegram(mensaje)
        return True
    else:
        print(f"[{datetime.now()}] Sin cupos disponibles (>= {PERSONAS_REQUERIDAS}) todavía.")
        return False


if __name__ == "__main__":
    encontrado = revisar_calendario()
    sys.exit(0 if not encontrado else 0)
