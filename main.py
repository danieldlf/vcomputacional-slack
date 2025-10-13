import os
import json
import time
import schedule

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

from src.api import PortalAPIClient
from src.services import group_by_restaurant
from src.slack import send_blocks
from src.log import Logger

logger = Logger().get_logger()

# Constante global de erro
UNCERTAINTY_RATE = 0.1

# Arquivo de estado persistente
STATE_FILE = "data/state.json"
CAPACITY_JSON = "data/capacities.json"

# Timezone local (ajuste se necessário)
TZ = ZoneInfo("America/Recife")

# Configuração das refeições
MEALS = [
    {"nome": "Café da Manhã", "start": "07:00", "end": "10:30", "interval_min": 30},
    {"nome": "Almoço",        "start": "12:00", "end": "15:30", "interval_min": 30},
    {"nome": "Jantar",        "start": "19:00", "end": "22:00", "interval_min": 30},
]

# Capacidades por restaurante (opcional via .env em JSON)
try:
    with open(CAPACITY_JSON, "r") as f:
        RESTAURANT_CAPACITY = json.load(f)
except Exception:
    RESTAURANT_CAPACITY = {}

# ------------------- Estado -------------------

def load_state():
    if os.path.exists(STATE_FILE):
        try:
            with open(STATE_FILE, "r") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_state(state):
    os.makedirs(os.path.dirname(STATE_FILE), exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, ensure_ascii=False, indent=2)

# ------------------- Funções principais -------------------

def ajustar_saidas(saidas: int, alpha: float = 0.15) -> int:
    """Aplica fator de correção nas saídas"""
    return round((1 - alpha) * saidas)

def process_interval(meal_name, start_dt, end_dt, state, capacities, alpha=0.15):
    """Processa um intervalo de 30 min"""
    client = PortalAPIClient()
    start_str = start_dt.strftime("%Y-%m-%dT%H:%M:%S")
    end_str = end_dt.strftime("%Y-%m-%dT%H:%M:%S")

    items = client.get_contagem_total(start_str, end_str)
    resumo = group_by_restaurant(items)

    today = datetime.now(TZ).strftime("%Y-%m-%d")
    state.setdefault(today, {}).setdefault(meal_name, {})

    blocks = [{"type": "header", "text": {"type": "plain_text", "text": f"{meal_name} — {start_dt.strftime('%H:%M')}–{end_dt.strftime('%H:%M')} - {today}"}}]

    for rest, vals in resumo.items():
        e = vals["entradas"]
        # s = ajustar_saidas(vals["saidas"], alpha)
        s = vals["saidas"]
        delta = e - s

        rest_state = state[today][meal_name].setdefault(rest, {
            "headcount": 0,
            "entradas": 0,
            "saidas": 0,
            "series": []
        })

        rest_state["headcount"] = max(0, rest_state["headcount"] + delta)
        rest_state["entradas"] += e
        rest_state["saidas"] += s
        rest_state["series"].append({
            "window": f"{start_dt.strftime('%H:%M')}–{end_dt.strftime('%H:%M')}",
            "entradas": e, "saidas": s, "delta": delta,
            "headcount": rest_state["headcount"]
        })

        cap = capacities.get(rest)
        margem = int(round(rest_state["headcount"] * UNCERTAINTY_RATE))
        headcount_txt = f"{rest_state['headcount']}"
        if cap:
            occ = round(100 * rest_state["headcount"] / cap)
            occ_margem = round(100 * margem / cap)
            occ_txt = f"{occ}% de {cap}"
        else:
            occ_txt = ""
        texto = (
            f"*{rest}*\n"
            f"Entradas: {rest_state['entradas']} | Saídas: {rest_state['saidas']}\n"
            f"Pessoas no restaurante: {headcount_txt}"
        )
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": texto}})
        blocks.append({"type": "divider"})

    logger.info(f"Processado {meal_name} {start_dt.strftime('%H:%M')}–{end_dt.strftime('%H:%M')}")
    save_state(state)
    send_blocks(blocks, os.getenv("SLACK_CHANNEL_ID"), text_fallback=f"{meal_name} — {start_dt.strftime('%H:%M')}–{end_dt.strftime('%H:%M')}")

def send_meal_summary(meal_name, state, capacities):
    """Envia fechamento da refeição"""
    today = datetime.now(TZ).strftime("%Y-%m-%d")
    meal_data = state.get(today, {}).get(meal_name, {})

    blocks = [{"type": "header", "text": {"type": "plain_text", "text": f"Fechamento — {meal_name} - {today}"}}]

    for rest, rstate in meal_data.items():
        totals_e = rstate["entradas"]
        totals_s = rstate["saidas"]
        totals_delta = totals_e - totals_s

        # Pico de fluxo (maior entradas em uma janela)
        if rstate["series"]:
            pico_fluxo = max(rstate["series"], key=lambda x: x["entradas"])
            pico_fluxo_txt = f"{pico_fluxo['window']} (Entradas: {pico_fluxo['entradas']})"
            pico_headcount = max(s["headcount"] for s in rstate["series"])
        else:
            pico_fluxo_txt = "—"
            pico_headcount = 0

        cap = capacities.get(rest)
        occ_peak = f" ({int(round(100*pico_headcount/cap))}% de {cap})" if cap else ""

        texto = (
            f"*{rest}*\n"
            f"Total Entradas: {totals_e} • Total Saídas: {totals_s}\n"
            f"Pico de fluxo: {pico_fluxo_txt}\n"
            f"Pico de pessoas: {pico_headcount}"
        )
        blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": texto}})
        blocks.append({"type": "divider"})

    logger.info(f"Enviado fechamento de {meal_name}")
    send_blocks(blocks, os.getenv("SLACK_CHANNEL_ID"), text_fallback=f"Fechamento {meal_name}")

# ------------------- Agendamento -------------------

def run_interval_job(meal_name, interval_min, state, capacities):
    now = datetime.now(TZ).replace(second=0, microsecond=0)
    start = now - timedelta(minutes=interval_min)
    process_interval(meal_name, start, now, state, capacities)

def run_meal_summary(meal_name, state, capacities):
    send_meal_summary(meal_name, state, capacities)

def setup_schedule(state, capacities):
    for meal in MEALS:
        start_h, start_m = map(int, meal["start"].split(":"))
        end_h, end_m = map(int, meal["end"].split(":"))
        interval = meal["interval_min"]

        t = datetime.now(TZ).replace(hour=start_h, minute=start_m, second=0, microsecond=0)
        end_t = t.replace(hour=end_h, minute=end_m)

        t = t + timedelta(minutes=interval)
        while t <= end_t:
            schedule.every().day.at(t.strftime("%H:%M")).do(
                run_interval_job, 
                meal_name=meal["nome"], 
                interval_min=interval, 
                state=state, 
                capacities=capacities
            )
            t += timedelta(minutes=interval)

        schedule.every().day.at(f"{end_h:02d}:{end_m:02d}").do(
            run_meal_summary, 
            meal_name=meal["nome"], 
            state=state, 
            capacities=capacities
        )

# ------------------- Main loop -------------------

def main():
    state = load_state()
    setup_schedule(state, RESTAURANT_CAPACITY)

    logger.info("Agendador iniciado...")
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()