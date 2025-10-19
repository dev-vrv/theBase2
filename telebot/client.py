import os
import json
import time
import urllib.parse
import urllib.request

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

if not TOKEN:
    raise RuntimeError("TELEGRAM_BOT_TOKEN not set")
if not CHAT_ID:
    raise RuntimeError("TELEGRAM_CHAT_ID not set")

BASE = f"https://api.telegram.org/bot{TOKEN}"

def _post(method: str, data: dict) -> dict:
    body = urllib.parse.urlencode(data, doseq=True).encode()
    req = urllib.request.Request(f"{BASE}/{method}", data=body)
    with urllib.request.urlopen(req, timeout=15) as r:
        res = json.loads(r.read().decode())
    if not res.get("ok"):
        raise RuntimeError(f"Telegram error: {res}")
    return res["result"]

def escape(s: str) -> str:
    return (s or "").replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")

def send_lead(name, phone, items, created_ts):
    created = time.strftime("%H:%M:%S", time.localtime(created_ts))
    text = (
        f"<b>Новая заявка The Base</b>\n"
        f"<b>Имя:</b> {escape(name)}\n"
        f"<b>Телефон:</b> {escape(phone)}\n"
        f"<b>Товар(ы):</b> {escape(', '.join(items))}\n"
        f"🕐 <b>Поступила:</b> {created}"
    )
    kb = {"inline_keyboard": [[{"text": "✅ Взять в работу", "callback_data": f"take:{created_ts}"}]]}
    res = _post("sendMessage", {
        "chat_id": CHAT_ID,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": json.dumps(kb, ensure_ascii=False)
    })
    return res["message_id"]

def edit_message(chat_id, message_id, new_text):
    _post("editMessageText", {
        "chat_id": chat_id,
        "message_id": message_id,
        "text": new_text,
        "parse_mode": "HTML"
    })

def answer_callback_query(cid, text=""):
    _post("answerCallbackQuery", {"callback_query_id": cid, "text": text})
